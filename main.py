import shutil
import socket
from urllib import request
from flask import *
from flask_restful import Api, Resource, abort, reqparse
import subprocess 
import os
import yaml
import requests




app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_SILENCE_UBER_WARNING'] = 1


###############################################################################################################################
#
#  class CreateNewBot  
###############################################################################################################################


class BotImplementations(Resource):

    def check_rasa_running(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            return True
        except socket.error as e:
            return False
        finally:
            s.close()
    def success_bot_message(self, port_number):

        print('came to succes bot message')
        while not self.check_rasa_running("localhost",int(port_number)):
            print("checking the server by localhost")
        return f"Server bot of {port_number} is running please start conversation", 201

    

    def create_domain(self, jsondata):

        dir_name = jsondata['port_number']

        intentsList = []
        actions = []
        forms = None
        slots = None
        entities = None

        # check if forms created
        if "forms" in jsondata:
            forms = jsondata["forms"]
    
        if "actons" in jsondata:
            actions = jsondata["actions"]

        # check if slots exist
        if "slots" in jsondata:
            slots = jsondata["slots"]

        # check if entities exist
        if "entities" in jsondata:
            entities = jsondata["entities"]

        if "intents" in jsondata:
            intentsList = jsondata["intents"]
        else:
            for intentsName in jsondata["nlu"]:
                intentsList.append(intentsName["intent"])

        data = {'version' : jsondata['version'] ,'intents' : intentsList ,  "responses" : jsondata['responses'] }

        cwd = os.getcwd()
        path =  cwd+f'/{dir_name}/domain.yml'
        # path =  f'/opt/app/{dir_name}/domain.yml'
        print(path)
        if os.access(path, os.R_OK):
            print('permission granted')
        else:
            print('no permission')
        with open( path, 'w') as yaml_file:
            yaml.dump(data, yaml_file, sort_keys = False)




    def create_rules(self, jsondata):
        dir_name = jsondata['port_number']
        data = {'version' : jsondata['version'] ,'rules' : jsondata['rules'] }
        cwd = os.getcwd()
        path = cwd+f'/{dir_name}/data/rules.yml'
        # path = f'/opt/app/{dir_name}/data/rules.yml'
        print(path)
        
        with open(path, 'w') as yaml_file:
            yaml.dump(data, yaml_file, sort_keys = False)



    def create_stories(self, jsondata):
        dir_name = jsondata['port_number']
        data = {'version' : jsondata['version'] ,'stories' : jsondata['stories'] }
        
        cwd = os.getcwd()
        path =  cwd+f'/{dir_name}/data/stories.yml'
        # path =  f'/opt/app/{dir_name}/data/stories.yml'
        print(path)
        
        with open(path, 'w') as yaml_file:
            yaml.dump(data, yaml_file, sort_keys = False)



    def create_nlu(self, jsondata):
        
        
        dir_name = jsondata['port_number']
        data = {'version' : jsondata['version'] ,'nlu' : jsondata['nlu'] }
        path = "/"+os.path.join(f'{dir_name}', 'data', 'nlu.yml')
        cwd = os.getcwd()
        path = cwd+path
        print("full path is : "+path)
        if os.access(path, os.R_OK):
            print('permission granted')
        else:
            print('no permission')
        # path = f'/opt/app/{dir_name}/data/nlu.yml'
        with open(path, 'w') as yaml_file:
            yaml.dump(data, yaml_file, sort_keys = False)
        print('read the file')
        with open(path, "r+") as f:
            contents = f.read()
            f.seek(0)
            f.write(contents.replace('examples:', 'examples: |'))
            f.truncate()

        with open(path, "r+") as f:
            contents = f.read()
            f.seek(0)
            f.write(contents.replace('  - ', '    - '))
            f.truncate()

    def initiate_script(self, port_number):
        try:
            cwd = os.getcwd()
            subprocess.run(['mkdir', '-p', f'{cwd}/{port_number}'],check=True)
            subprocess.run([ 'cp','-r',f'{cwd}/base/.',f'{cwd}/{port_number}/.'],check=True)
            subprocess.call([ 'chmod', '-R', '777', f'{cwd}/{port_number}/.'])
        except subprocess.CalledProcessError as e:
            return e, 400
       
    def runBot(self, port_number):
        cwd = os.getcwd()
        path = cwd+f'/{port_number}'
        os.chdir(path)

        try:
            
            # p = multiprocessing.Process(target=self.run_rasa, args=(port_number,))
            # p.start()
            subprocess.Popen(['rasa', 'run', '--enable-api', '--port', f'{port_number}'])
        except subprocess.CalledProcessError as exc:
            os.chdir(cwd)            
            return exc, 204

        os.chdir(cwd)
        return self.success_bot_message(port_number)


    def kill_bot_server(self, port_number):
        output = subprocess.run(["lsof", "-i", f":{port_number}"], stdout=subprocess.PIPE)

        for line in output.stdout.decode().splitlines():
            if "LISTEN" in line:
                # Split the line into fields and get the PID
                fields = line.split()
                pid = fields[1]
                print(f"The server with port {port_number} has PID: {pid}")
                try:
                    process = subprocess.run(["kill", "-9", f"{pid}"],check=True)
                    print(process)
                    return True
                except subprocess.CalledProcessError as exc:
                    return exc, 204

                
                
        
    def train_and_run_bot(self, port_number):
        cwd = os.getcwd()
        print(f'current path {cwd}')
        path = cwd+f'/{port_number}'
        os.chdir(path)
        print(f'rasa path {path}')
        try:
            process = subprocess.run([  'rasa','train'])
        except subprocess.CalledProcessError as exc:
            os.chdir(cwd)            
            return exc, 204
        os.chdir(cwd)   
        return self.runBot(port_number)



    def create_new_bot(self, jsondata):
        initiate = self.initiate_script(jsondata["port_number"])


        self.create_nlu(jsondata)
        self.create_rules(jsondata)
        self.create_stories(jsondata)
        self.create_domain(jsondata)
        return f"bot with "+jsondata['port_number']+" port number has been created successfully", 201



###############################################################################################################################
#
#  class CreateNewBot  
###############################################################################################################################


class CreateNewBot(Resource):

    def get(self, port_number):
        botImp = BotImplementations()
        if botImp.check_rasa_running("localhost", int(port_number)):
            return f"server for bot number {port_number} is already running", 409
        return botImp.runBot(port_number)

    def post(self):
        print("creating new bot")
        jsondata = request.get_json()
        if os.path.exists(f'./{jsondata["port_number"]}'):
            return "Bot with this port number already exists", 403
        botImp = BotImplementations()
        return botImp.create_new_bot(jsondata)


###############################################################################################################################
#
#  class Bot  
###############################################################################################################################

class Bot(Resource):

    def get(self, port_number):
        botImp = BotImplementations()
        if botImp.check_rasa_running("localhost", int(port_number)):
            print(f'port {port_number} is running')
            if botImp.kill_bot_server(port_number):

                return botImp.train_and_run_bot(port_number)
            else:
                return f"Unable to stop {port_number} bot", 409
        else:
            return botImp.train_and_run_bot(port_number)

###############################################################################################################################
#
#  class Rasa  
###############################################################################################################################


class Rasa(Resource):

    def get(self, file_name, port_number ):

        if file_name == "domain" or file_name == "config" :
            dir_name = "./"+port_number+"/"+file_name+".yml" 
        elif file_name == "nlu" or file_name == "rules" or file_name == "stories":
            dir_name = "./"+port_number+"/data/"+file_name+".yml" 
        else:
            return "file name is incorrect"

        with open(dir_name, 'r') as stream:
            try:
                parsed_yaml=yaml.safe_load(stream)
                print(type(parsed_yaml))
            except yaml.YAMLError as exc:
                return exc, 204

        return parsed_yaml, 200


    def put(self,file_name, port_number ):

        cwd = os.getcwd()
        jsondata = request.get_json()
        parsed_yaml = []
        if file_name == "domain" or file_name == "config" :
            dir_name = cwd+"/"+port_number+"/"+file_name+".yml" 
        elif file_name == "nlu" or file_name == "rules" or file_name == "stories":
            dir_name = cwd+"/"+port_number+"/data/"+file_name+".yml" 
        else:
            return "file name is incorrect", 400

        with open(dir_name, 'r') as stream:
            try:
                parsed_yaml=yaml.safe_load(stream)
                
            except yaml.YAMLError as exc:
                return exc, 204

        match file_name:
            case "domain":
                parsed_yaml['responses'] = dict(list(parsed_yaml['responses'].items())+ list(jsondata['responses'].items()))
                with open(dir_name , 'w') as yaml_file:
                    yaml.dump(parsed_yaml, yaml_file, sort_keys = False)
                return f'responces updated succesfully on domain bot {port_number}', 200
            case "stories":
                return self.update_stories(jsondata, port_number, parsed_yaml)

            case "rules":
                return self.update_rules(jsondata, port_number, parsed_yaml)

            case "nlu":
                return self.update_nlu(jsondata, port_number)
            case _:
                return "wrong file name", 404

    def delete(self, port_number):

        shutil.rmtree(port_number)
        if os.path.exists(port_number):
            return f"unable to delete {port_number} bot server", 202
        botImp = BotImplementations()
        if botImp.check_rasa_running("localhost", int(port_number)):
            print(f'port {port_number} is running')
            if not botImp.kill_bot_server(port_number):
                return f"Bot deleted but unable to stop {port_number} bot server", 202
        return f'Bot no {port_number} deleted successfully', 200

    def update_stories(self, jsondata, port_number, parsed_stories):
        # check if utter response exist in domain 
        domain_yaml = self.domain_file( port_number)
        for steps in jsondata['steps']:
            for step in steps.keys():
                if step == "action":
                    if steps['action'] not in domain_yaml['responses'].keys():
                        return 'action '+steps['action'] +' does not exist in domain file', 403
        parsed_stories["stories"].append(jsondata)
        
        with open(os.getcwd()+"/"+port_number+"/data/stories.yml" , 'w') as yaml_file:
            yaml.dump(parsed_stories, yaml_file, sort_keys = False)
        return f'stories updated succesfully on bot {port_number}', 200

    def update_rules(self, jsondata, port_number, parsed_rules):
        # check if utter response exist in domain
        print(jsondata) 
        domain_yaml = self.domain_file( port_number)
        for steps in jsondata['steps']:
            for step in steps.keys():
                if step == "action":
                    if steps['action'] not in domain_yaml['responses'].keys():
                        return 'action '+steps['action'] +' does not exist in domain file', 403
        
        parsed_rules["rules"].append(jsondata)
        with open(os.getcwd()+"/"+port_number+"/data/stories.yml" , 'w') as yaml_file:
            yaml.dump(parsed_rules, yaml_file, sort_keys = False)

        return f'rules updated succesfully on bot {port_number}', 200

    def update_nlu(self, jsondata, port_number):

        cwd = os.getcwd()
        list_file = []
        list_file.append(jsondata)
        with open(cwd+"/"+port_number+"/data/nlu.yml" , 'a') as yaml_file:
            yaml.dump(list_file, yaml_file, sort_keys = False)



        with open(cwd+f"/{port_number}/data/nlu.yml", "r+") as f:
            contents = f.read()
            f.seek(0)
            f.write(contents.replace('examples:', 'examples: |'))
            f.truncate()

        with open(cwd+f'/{port_number}/data/nlu.yml', "r+") as f:
            contents = f.read()
            f.seek(0)
            f.write(contents.replace('    - ', '  - '))
            f.truncate()
        with open(cwd+f"/{port_number}/data/nlu.yml", "r+") as f:
            contents = f.read()
            f.seek(0)
            f.write(contents.replace('| |', '|'))
            f.truncate()
        with open(cwd+f'/{port_number}/data/nlu.yml', "r+") as f:
            contents = f.read()
            f.seek(0)
            f.write(contents.replace('  - ', '    - '))
            f.truncate()
        return f'NLU updated succesfully on bot {port_number}', 200
    # pars domain file 
    def domain_file(self, port_number):
        with open(os.getcwd()+"/"+port_number+"/domain.yml" , 'r') as stream:
            try:
                domain_yaml =yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                return exc
        print(domain_yaml['responses'].keys())
        return domain_yaml


###############################################################################################################################
#
#  class CreateNewBot  
###############################################################################################################################


class ResetCWD(Resource):

    def get(self):
        os.chdir('/opt/app/')
        return f'Current Working Directory changed to {os.getcwd()}', 200 



api.add_resource(Rasa, "/rasa/<string:file_name>/<string:port_number>")
api.add_resource(Rasa, "/rasa/<string:port_number>", endpoint='/rasa/<string:port_number>')
api.add_resource(CreateNewBot, '/new_bot')
api.add_resource(ResetCWD, '/reset_cwd')
api.add_resource(CreateNewBot,"/run_bot/<string:port_number>", endpoint= '/run_bot/<string:port_number>')
api.add_resource(Bot,"/run_train_bot/<string:port_number>", endpoint= '/run_train_bot/<string:port_number>')




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
