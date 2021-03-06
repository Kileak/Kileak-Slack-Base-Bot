import pickle
import re

from bottypes.remoteserver import *
from bottypes.command_descriptor import *
from handlers.handler_factory import *
from handlers.base_handler import *
from util.util import *


class AddServerCommand(Command):

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]

        if len(args)>1:
            alias = args[1]
        else:
            alias = ""

        server = RemoteServer(name, alias)

        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))
        except:
            serverlist = {}


        if not name in serverlist:
            serverlist[name] = server

            message = "Added remote server `{}`".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")
        else:
            message = "Couldn't add server `{}` (Already in list)".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")

        pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))
        
class SetAliasCommand(Command):

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]
        alias = args[1]

        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))
        except:
            serverlist = {}

        if name in serverlist:
            serverlist[name].setalias(alias)
            
            message = "Set alias for server: `{}` => `{}`".format(name, alias)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")
        else:
            message = "Couldn't set alias for server `{}` (Not in list)".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")

        pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))  

class RemoveServerCommand(Command):

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]
        
        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))
        except:
            serverlist = {}

        if name in serverlist:
            del serverlist[name]
            
            message = "Removed remote server `{}`".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")
        else:
            message = "Couldn't remove server `{}` (Not in list)".format(name)
            slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")

        pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))

class RequestServerCommand(Command):

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]
        
        server = None

        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))

            for s in serverlist:                
                test = serverlist[s]

                if s == name or test.alias == name:
                    server = serverlist[s]
                    break
        except:
            serverlist = {}
            server = None

        if server != None:
            if server.occupied:
                message = "Remote server is already occupied by: *{}*".format(transliterate(server.occupiedBy))
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True)                
            else:
                print (user_id)
                member = get_member(slack_client, user_id)

                server.occupied = True
                server.occupiedBy = member['user']['name']

                message = "Remote server `{}` is reserved for you".format(server.name)
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True)                

                pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))
        else:
                message = "Remote server `{}` doesn't exist.".format(name)
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True)                

        print (channel_id)
        message = "*======== Server status ========*\n"
        
        for server in serverlist:
            if serverlist[server].occupied:
                message += ":no_entry_sign: *{}* ({}) - {}\n".format(server, serverlist[server].alias, transliterate(serverlist[server].occupiedBy))
            else:
                message += ":white_check_mark: *{}* ({}) - free \n".format(server, serverlist[server].alias)

        # Notify people of new channel        
        slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")


class ReleaseServerCommand(Command):

    def execute(self, slack_client, args, channel_id, user_id):
        name = args[0]
        
        server = None

        try:
            serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))

            for s in serverlist:                
                test = serverlist[s]

                if s == name or test.alias == name:
                    server = serverlist[s]
                    break
        except:
            serverlist = {}
            server = None

        if server != None:
            if server.occupied:
                server.occupied = False
                server.occupiedBy = ""

                message = "Remote server is released: {}".format(server.name)
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")                

                pickle.dump(serverlist, open(RemoteServerHandler.DB, "wb"))
            else:
                message = "Remote server isn't occupied, no need to release"
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")                
        else:
                message = "Remote server `{}` doesn't exist.".format(name)
                slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")                

        print (channel_id)

        message = "*======== Server status ========*\n"
        
        for server in serverlist:
            if serverlist[server].occupied:
                message += ":no_entry_sign: *{}* ({}) - {}\n".format(server, serverlist[server].alias, transliterate(serverlist[server].occupiedBy))
            else:
                message += ":white_check_mark: *{}* ({}) - free \n".format(server, serverlist[server].alias)

        # Notify people of new channel        
        slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")

        

class RemoteServerStatusCommand(Command):

    def execute(self, slack_client, args, channel_id, user_id):        
        serverlist = pickle.load(open(RemoteServerHandler.DB, "rb"))

        print (channel_id)
        message = "*======== Server status ========*\n"
        
        for server in serverlist:
            if serverlist[server].occupied:
                message += ":no_entry_sign: *{}* ({}) - {}\n".format(server, serverlist[server].alias, transliterate(serverlist[server].occupiedBy))
            else:
                message += ":white_check_mark: *{}* ({}) - free \n".format(server, serverlist[server].alias)

        # Notify people of new channel        
        slack_client.api_call("chat.postMessage", channel=channel_id, text=message.strip(), as_user=True, parse="full")

class RemoteServerHandler(BaseHandler):

    DB = "databases/remoteserver_handler.bin"
    
    def __init__(self):
        self.commands = {
            "addserver": CommandDesc(AddServerCommand, "Adds a new server to watch", ["server_name"], ["alias"]),
            "setalias": CommandDesc(SetAliasCommand, "Sets an alias for a server", ["server_name", "alias"], None),
            "removeserver": CommandDesc(RemoveServerCommand, "Removes a server to watch", ["server_name"], None),
            "r" : CommandDesc(RequestServerCommand, "Request server access", ["server_name"], None),
            "f" : CommandDesc(ReleaseServerCommand, "Release a server access", ["server_name"], ["force"]),            
            "status" : CommandDesc(RemoteServerStatusCommand, "Show server status", None, None)
        }


    def init(self, slack_client, bot_id):
        # Find channels generated by challenge_handler
        database = []
        

# Register this handler
HandlerFactory.register("server", RemoteServerHandler())
