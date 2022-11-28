import sys
import os
import json
import psycopg2
import pandas as pd


argv = open(sys.argv[1])
json_data = json.load(argv)

class Services:

    def dataset(self,dataset_data):
        """Extracting the Dataset name from the dataset_data and returning only dataset name

        Args:
            dataset_data ([Dictionary]): "typeProperties": {
                            "source": {
                                "type": "SqlServerSource",
                                "sqlReaderQuery": "select id, Tablename,query,JSON_VALUE(PK,'$.pk_col') pk_col ,LMD,Success from Metadata",
                                "queryTimeout": "02:00:00",
                                "partitionOption": "None"
                            },
                            "dataset": {
                                "referenceName": "SqlServerTable1",
                                "type": "DatasetReference",
                                "parameters": {}
                            },
                            "firstRowOnly": false
                        }

        Returns:
            [String]: dataset name or None value
        """
        try:
            dataset_data.get("typeProperties").get('dataset')
            data = dataset_data.get('typeProperties').get('dataset').get('referenceName')
        except:
            data = None
        
        return data

    def linked_service(self,linked_service_data):
        """Extracting the Linked Service name from the linked_service_data and returning only linked service name

        Args:
            linked_service_data ([dictionary]): "name": "Stored procedure1",
                                    "type": "SqlServerStoredProcedure",
                                    "dependsOn": [
                                        {
                                            "activity": "Data flow1",
                                            "dependencyConditions": [
                                                "Succeeded"
                                            ]
                                        }
                                    ],
                                    "policy": {
                                        "timeout": "7.00:00:00",
                                        "retry": 0,
                                        "retryIntervalInSeconds": 30,
                                        "secureOutput": false,
                                        "secureInput": false
                                    },
                                    "userProperties": [],
                                    "typeProperties": {
                                        "storedProcedureName": "[dbo].[Success_Fail]",
                                        "storedProcedureParameters": {
                                            "id": {
                                                "value": {
                                                    "value": "@item().id",
                                                    "type": "Expression"
                                                },
                                                "type": "Int32"
                                            },
                                            "LMD": {
                                                "value": {
                                                    "value": "@variables('Time')",
                                                    "type": "Expression"
                                                },
                                                "type": "String"
                                            },
                                            "sorf": {
                                                "value": "S",
                                                "type": "String"
                                            }
                                        }
                                    },
                                    "linkedServiceName": {
                                        "referenceName": "SqlServer1",
                                        "type": "LinkedServiceReference"
                                    }

        Returns:
            [String]: linked service name or None
        """

        try:
            linked_service_data.get('linkedServiceName')
            data = linked_service_data.get('linkedServiceName').get('referenceName')
        except:
            data = None
    
        return data

    def copy_activity_datasets(self,copy_data):
        """Extracting the Dataset name from the Copy Activity and returning only Input Dataset Name and Output Dataset name

        Args:
            copy_data ([dictionary]): {
                "name": "copy to adls gen 2",
                "type": "Copy",
                "dependsOn": [],
                "policy": {
                    "timeout": "7.00:00:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                },
                "userProperties": [],
                "typeProperties": {
                    "source": {
                        "type": "DelimitedTextSource",
                        "storeSettings": {
                            "type": "AzureBlobFSReadSettings",
                            "recursive": true,
                            "enablePartitionDiscovery": false
                        },
                        "formatSettings": {
                            "type": "DelimitedTextReadSettings"
                        }
                    },
                    "sink": {
                        "type": "DelimitedTextSink",
                        "storeSettings": {
                            "type": "AzureBlobFSWriteSettings"
                        },
                        "formatSettings": {
                            "type": "DelimitedTextWriteSettings",
                            "quoteAllText": true,
                            "fileExtension": ".txt"
                        }
                    },
                    "enableStaging": false,
                    "translator": {
                        "type": "TabularTranslator",
                        "typeConversion": true,
                        "typeConversionSettings": {
                            "allowDataTruncation": true,
                            "treatBooleanAsNumber": false
                        }
                    }
                },
                "inputs": [
                    {
                        "referenceName": "src",
                        "type": "DatasetReference",
                        "parameters": {}
                    }
                ],
                "outputs": [
                    {
                        "referenceName": "dest",
                        "type": "DatasetReference",
                        "parameters": {}
                    }
                ]
            }

        Returns:
            [dictionary]: {'input_copy_dataset':'input_copy_dataset_name'
                            'output_copy_dataset':'output_copy_dataset_name'}
        """
        response = {}
        try:
            copy_data.get('inputs')
            response['input_copy_dataset'] = copy_data.get('inputs')[0].get('referenceName')
            response['output_copy_dataset'] = copy_data.get('outputs')[0].get('referenceName')
        except:
            response['input_copy_dataset'] = None
            response['output_copy_dataset'] = None
        return response

    def helper(self,pipeline_name,activities,nested_activities=None):
        """the helper function will transform the each pipeline data into dictionary format and return the json output

        Args:
            pipeline_name ([String]): It accepts a string data which contains pipeline name
            activities ([dictionary]): It contains Json data which do not have any nested data
            nested_activities ([dictionary], optional): [It contains Json data which have nested data default is None]. Defaults to None.

        Returns:
            [dictionary]: [Transform all the give input into Activities pipeline data \
                 and Nested activities pipeline data individually and return the values]
        """
        pipeline = {}
        pipeline['pipeline_name'] = pipeline_name
        # activities['name'] object will return name of the activity
        # activities['type'] object will return type of the activity
        pipeline['activity_name'] = activities['name']
        pipeline['activity_type'] = activities['type']
        try:
            # Extracting Input and Output Datasets from Copy Activity
            ds = self.copy_activity_datasets(nested_activities)
            pipeline['nested_activity_name'] = nested_activities['name']
            pipeline['nested_activity_type'] = nested_activities['type']
            pipeline['dataset_name'] = self.dataset(nested_activities)
            pipeline['linked_service_name'] = self.linked_service(nested_activities)
            pipeline['input_copy_dataset'] = ds.get('input_copy_dataset')
            pipeline['output_copy_dataset'] = ds.get('output_copy_dataset')
        except:
            # Extracting Input and Output Datasets from Copy Activity
            ds = self.copy_activity_datasets(activities)
            pipeline['nested_activity_name'] = None
            pipeline['nested_activity_type'] = None
            pipeline['dataset_name'] = self.dataset(activities)
            pipeline['linked_service_name'] = self.linked_service(activities)
            pipeline['input_copy_dataset'] = ds.get('input_copy_dataset')
            pipeline['output_copy_dataset'] = ds.get('output_copy_dataset')
            
        return pipeline

class Database:
    """ Creating Instance for Database 
    """
    def db_connection(self,host,user,password,database,port):
        """Creating connection to the PostgreSQL Databases and

        Args:
            database ([String]): 'training_db'
            user ([String]): 'postrgres'
            password ([String]): 'Datasturdy123#'
            host ([String]): 'kafka-demo-002'
            port ([String]): 5432

        Returns:
            [Class]: [DB Connection]
        """
        self.connection = psycopg2.connect(
                database='training_db',
                user='postgres',
                password='Datasturdy123#',
                host='kafka-demo-002',
                port=5432)

        self.cursor = self.connection.cursor()

        return self.connection

    def insert_data(self,pipeline):
        """Inserting the data into PostgreSQL Database with the following Json data \
            and it will not return any object
        Args:
            pipeline ([dictionary]): {
                'pipeline_name':'pipeline1',
                'activity_name':'Wait1',
                'activity_type':'Wait',
                'nested_activity_name':None,
                'nested_activity_type':None,
                'dataset_name':'Sql',
                'linked_service_name:'ls_1',
                'input_copy_dataset':'input1',
                'input_copy_dataset':'input_copy_dataset1'}
        """
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
    db.db_connection('kafka-demo-002','postgres','Datasturdy123#','training_db',5432)
    service = Services()

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
                    pipeline = service.helper(data['name'],activities,nested_activities)
                    response.append(pipeline)
                    db.insert_data(pipeline)
            # If nested activity is not available then outer activity
            else:
                pipeline = service.helper(data['name'],activities)
                response.append(pipeline)
                db.insert_data(pipeline)
                
   
    df = pd.DataFrame(response)
    print(df)
    directory = 'C:'
    # df.to_csv(f'{directory}\\Datasturdy\\test.csv',index=False)