import argparse
import os
import json

from generator import PojoGenerator
from restapi import ApiClient

SOBJECTS_FILE_NAME = "sobjects.json"

parser = argparse.ArgumentParser(description='Salesforce OAuth2 Client')
parser.add_argument('-u', '--username', help='Salesforce admin name', required=True)
parser.add_argument('-p', '--password', help='Salesforce admin password', required=True)
parser.add_argument('-c', '--client_id', help='Salesforce client id', required=True)
parser.add_argument('-s', '--client_secret', help='Salesforce client secret', required=True)

args = parser.parse_args()

sobjects = None
api_client = ApiClient(args.username, args.password, args.client_id, args.client_secret)


def get_available_sobjects():
    global sobjects
    sobjects = api_client.get_sobjects()
    with open(SOBJECTS_FILE_NAME, "w") as file:
        file.write(json.dumps(sobjects))


if os.path.exists(SOBJECTS_FILE_NAME):
    answer = input("You already have a file with sobjects. Would you like to overwrite it? (y/n)")
    if answer == "y":
        get_available_sobjects()
    elif answer == "n":
        sobjects = json.load(open(SOBJECTS_FILE_NAME))
    else:
        print("Invalid answer. Exiting...")
        exit(1)
else:
    get_available_sobjects()

if not os.path.exists("pojos"):
    os.mkdir("pojos")

object_names = [sobject["name"] for sobject in sobjects]
print("Available SObjects: ")
print("\n".join(object_names))

while True:
    print("Enter the name(s) of the sobject(s) to generate POJO. For example: Account, Visit__c, etc.")
    print("To exit the program enter 'exit' or 'quit'.")
    user_input = input().replace(" ", "").split(",")
    if "exit" in user_input or "quit" in user_input:
        break
    for sobject_name in user_input:
        if sobject_name not in object_names:
            print(f"SObject {sobject_name} not found")
            continue
        sobject_description = api_client.get_sobject_description(sobject_name)
        if "APXT_Redlining__" in sobject_name:
            sobject_name = sobject_name.replace("APXT_Redlining__", "")

        class_name = sobject_name if '__c' not in sobject_name else sobject_name[:-3]
        class_name = class_name.replace("_", "")

        pojo_generator = PojoGenerator(class_name, sobject_description["fields"])
        pojo_generator.generate_pojo()

        if os.path.exists(f"pojos/{class_name}.java"):
            print(f"POJO {class_name}.java was successfully generated with dependent enums")
        else:
            print(f"POJO {class_name}.java generation failed.")
            exit(-1)

print("Terminating program. Goodbye.")
exit(0)
