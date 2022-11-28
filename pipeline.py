import sys
import os
import json
import psycopg2
import pandas as pd



argv = open(sys.argv[1])
json_data = json.load(argv)


def dataset(dataset_data):
    try:
        dataset_data.get("typeProperties").get('dataset')
        data = dataset_data.get('typeProperties').get('dataset').get('referenceName')
    except:
        data = None
    
    return data



def linked_service(linked_service_data):

    try:
        linked_service_data.get('linkedServiceName')
        data = linked_service_data.get('linkedServiceName').get('referenceName')
    except:
        data = None
   
    return data


def copy_inputs(input_data):
    try:
        input_data.get('inputs')
        data = input_data.get('inputs')[0].get('referenceName')
    except:
        data =None
    return data

def copy_output(output_data):
    
    try:
        output_data.get('outputs')
        data = output_data.get('outputs')[0].get('referenceName')
    except:
        data = None
    
    return data

class Database:

    def db_connection(self):
        self.connection = psycopg2.connect(
                database='training_db',
                user='postgres',
                password='Datasturdy123#',
                host='kafka-demo-002',
                port=5432)

        self.cursor = self.connection.cursor()

    def insert_data(self,pipeline):
        print(pipeline,"pipelineee")
        query = "INSERT INTO public.pipeline (pipeline_name,activity_name,activity_type,nested_activity_name,nested_activity_type,\
                dataset_name,linked_service_name,input_copy_dataset,output_copy_dataset)\
                    VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                    pipeline['pipeline_name'],
                    pipeline['activity_name'],
                    pipeline['activity_type'],
                    pipeline['nested_activity_name'],
                    pipeline['nested_activity_type'],
                    pipeline['dataset_name'],
                    pipeline['linked_service_name'],
                    pipeline['input_copy_dataset'],
                    pipeline['output_copy_dataset'])
        
        self.cursor.execute(query)
        self.connection.commit()

if __name__ == '__main__':
    db = Database()
    db.db_connection()
    response = []
    # Iterating Each Pipeline
    for data in json_data['value']:
        # data['name'] object will return pipeline name
        
        # Iterating each activity in one Pipeline
        for activities in data['properties']['activities']:
            # activities['name'] object will return name of the activity
            # activities['type'] object will return type of the activity
            # Checking any Nested activities in Pipeline
            if activities['typeProperties'].get('activities') != None:
                
                # loop through each nested activity
                # nested_activities['name'] object will return name of the nested_activity
                # nested_activities['type'] object will return type of the nested_activity
                for nested_activities in activities['typeProperties'].get('activities'):
                    pipeline = {}
                    pipeline['pipeline_name'] = data['name']
                    pipeline['activity_name'] = activities['name']
                    pipeline['activity_type'] = activities['type']
                    pipeline['nested_activity_name'] = nested_activities['name']
                    pipeline['nested_activity_type'] = nested_activities['type']
                    pipeline['dataset_name'] = dataset(nested_activities)
                    pipeline['linked_service_name'] = linked_service(nested_activities)
                    pipeline['input_copy_dataset'] = copy_inputs(nested_activities)
                    pipeline['output_copy_dataset'] = copy_output(nested_activities)
                    # print(pipeline)
                    response.append(pipeline)
                    db.insert_data(pipeline)
                # If nested activity is not available then outer activity
            else:
                pipeline = {}
                pipeline['pipeline_name'] = data['name']
                # activities['name'] object will return name of the activity
                # activities['type'] object will return type of the activity
                pipeline['activity_name'] = activities['name']
                pipeline['activity_type'] = activities['type']
                pipeline['nested_activity_name'] = None
                pipeline['nested_activity_type'] = None
                pipeline['dataset_name'] = dataset(activities)
                pipeline['linked_service_name'] = linked_service(activities)
                pipeline['input_copy_dataset'] = copy_inputs(activities)
                pipeline['output_copy_dataset'] = copy_output(activities)
                # print(pipeline)
                response.append(pipeline)
                db.insert_data(pipeline)
                
    # print(response)
    df = pd.DataFrame(response)
    directory = 'C:'
    print(df)
    # df.to_csv(f'{directory}\\Datasturdy\\test.csv',index=False)