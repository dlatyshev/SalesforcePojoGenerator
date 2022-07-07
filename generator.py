types_map = {
    "id": "String",
    "string": "String",
    "reference": "String",
    "datetime": "LocalDateTime",
    "boolean": "Boolean",
    "double": "Double",
    "location": "String",
    "textarea": "String",
    "date": "LocalDate",
    "address": "String",
    "phone": "String",
    "url": "String",
    "currency": "Double",
    "int": "Integer",
    "percent": "Double",
    "time": "LocalDateTime",
    "email": "String",
}


class PojoGenerator:

    def __init__(self, class_name: str, fields: dict):
        self.class_name = class_name
        self.fields = fields

    def generate_pojo(self, class_access_level="public", method_access_level="private",
                      package_name="com.salesforce.sobjects"):
        with open(f"pojos/{self.class_name}.java", "w") as file:
            file.write(f"package {package_name};\n\n")
            file.write("@NoArgsConstructor\n")
            file.write("@AllArgsConstructor\n")
            file.write("@Data\n")
            file.write("@Builder\n")
            file.write(f"{class_access_level} class {self.class_name} {{\n\n")
            for field in self.fields:
                file.write(f"\t@JsonProperty(\"{field['name']}\")\n")
                try:
                    field_type = field['type']
                    field_name = field['name']
                    if "APXT_Redlining__" in field_name:
                        field_name = field_name.replace("APXT_Redlining__", "")

                    if field_type == "picklist" or field_type == "multipicklist":
                        enum_name = self.class_name + field_name.replace(" ", "").replace("-", "").replace(".", "")
                        if "__c" in enum_name or "__r" in enum_name:
                            enum_name = enum_name[:-3]
                            enum_name = "".join([word.capitalize() if word.islower() else word for word in enum_name.split("_")])
                        self.__generate_enum(enum_name, field, package_name)
                        if field_type == "picklist":
                            file.write(f"\t{method_access_level} {enum_name} {self.__generate_field_name(field_name)};\n\n")
                        else:
                            file.write(f"\t{method_access_level} Set<{enum_name}> {self.__generate_field_name(field_name)};\n\n")
                    else:
                        file.write(f"\t{method_access_level} {types_map[field_type]} {self.__generate_field_name(field_name)};\n\n")
                except KeyError:
                    print(f"The field of type {field['type']} is not supported yet. Please, add it to the types_map.")
            file.write("}\n")

    @staticmethod
    def __generate_field_name(raw_field_name: str) -> str:
        words = raw_field_name.replace("__c", "").replace("__s", "").split("_")
        words = filter(lambda word: word != "", words)
        field_name = "".join([word[0].upper() + word[1:] if not word.isupper() else word for word in words])
        return field_name[0].lower() + field_name[1:] if not field_name.isupper() else field_name

    def __generate_enum(self, enum_name: str, field: dict, package_name: str):
        with open(f"pojos/{enum_name}.java", "w") as file:
            file.write(f"package {package_name};\n\n")
            file.write(f"public enum {enum_name} implements Picklist {{\n\n")
            for idx, constant in enumerate(field['picklistValues']):
                constant_name = constant['label']\
                    .replace(" ", "_").replace("-", "_").replace(".", "")\
                    .replace("'", "").replace("`", "").replace("/", "OR")\
                    .replace("´", "")\
                    .upper()
                if constant_name.isdigit():
                    constant_name = f"{self.class_name}_{constant_name}"
                if idx != len(field['picklistValues']) - 1:
                    file.write(f"""\t{constant_name}("{constant['label']}", "{constant['value']}"),\n""")
                else:
                    file.write(f"""\t{constant_name}("{constant['label']}", "{constant['value']}");\n\n""")

            file.write(f"""\tprivate final String value;\n""")
            file.write(f"""\tprivate final String apiName;\n\n""")

            file.write(f"""\t{enum_name}(String value, String apiName) {{\n""")
            file.write(f"""\t\tthis.value = value;\n""")
            file.write(f"""\t\tthis.apiName = apiName;\n""")
            file.write(f"""\t}}\n\n""")

            file.write(f"""\tpublic String getValue() {{\n""")
            file.write(f"""\t\treturn value;\n""")
            file.write(f"""\t}}\n\n""")

            file.write("\t@JsonValue\n")
            file.write(f"""\tpublic String getApiName() {{\n""")
            file.write(f"""\t\treturn apiName;\n""")
            file.write(f"""\t}}\n\n""")

            file.write("}\n")
