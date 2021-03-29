import os

import avro.schema
import csv
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
from hdfs import InsecureClient

client = InsecureClient('http://192.168.56.101:50070', user='cloudera')
file_name = "airlines"
result_file_path = file_name + ".avro"


def read_csv_from_hdfs(schema):
    with client.read('/user/student/' + file_name + '/' + file_name + '.dat', encoding='latin') as reader:
        csv_data = csv.reader(reader, delimiter=',')
        for line in csv_data:
            yield dict(zip(schema.fields_dict.keys(), line))


def convert_file_to_avro():
    schema = avro.schema.parse(open(file_name + ".avsc").read())
    data = read_csv_from_hdfs(schema)
    writer = DataFileWriter(open(result_file_path, "wb"), DatumWriter(), schema, codec='deflate')
    for count, row in enumerate(data):
        try:
            writer.append(row)
        except IndexError:
            print("Something is wrong in {0}".format(row))
    writer.close()


def remove_local_file():
    if os.path.exists(result_file_path):
        os.remove(result_file_path)
    else:
        print("The file does not exist")


def read_convert_and_write_file():
    hdfs_folder = "/user/student/" + file_name + "/"
    convert_file_to_avro()
    client.upload(hdfs_folder, result_file_path)
    remove_local_file()


read_convert_and_write_file()
