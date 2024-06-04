class Version:
    version_id = None
    name = "Holy Bible"
    custom_copyright_statement = None

    def __init__(self, version_id, version_information_file="custom_version_info.txt"):
        self.version_id = version_id
        with open(version_information_file) as f:
            for line_no, line in enumerate(f.readlines()):
                parts = line.strip().split(";")
                if len(parts) != 3:
                    print(f"Invalid version info file at line {line_no}. Expected '<version_id>;<name>;<copyright statement>', got '{line.strip()}'.")
                    continue
                if parts[0] == str(version_id):
                    self.name, self.custom_copyright_statement = parts[1:]
        if self.custom_copyright_statement == None:
            print(f"Version information for version_id {self.version_id} missing, using defaults.")
    
    def __str__(self):
        return str(self.version_id)