#!/usr/bin/env python3
import re
import zomboid_rcon

class ZomboidServer:

	conn = None

	def __init__(self, ip, port, password):
		self.conn = zomboid_rcon.ZomboidRCON(ip=server_ip, port=server_port, password=server_password)


	def _command(self, command, *args):
		return self.conn.command(command, *args).response

	def _isValid_playerName(self, name):
		if not name == name.strip():
			return False
		return True

	def onlinePlayers(self):
		res = self._command("players")
		
		# Split the input text by lines
		lines = res.split('\n')

		# Use regex to extract the number of players from the first line
		online_players = re.search(r'Players connected \((\d+)\):', lines[0].strip())
		if not online_players:
			return None
		online_players = int(online_players.group(1))

		# Extract player names from the lines after the first one
		players = [line.strip()[1:].strip() for line in lines[1:] if line.startswith('-')]

		# Validate if the number of players matches the number listed
		if len(players) != online_players:
			return None

		return players

	def healPlayer(self, player):
		if not self._isValid_playerName(player):
			return False

		res = self._command("godmode", player)

		# If invalid response return
		if not res.startswith("User "):
			return False
		# If user was not found
		if res.endswith(" not found."):
			return False
		
		# Heal player by making him god and back human
		max_tries = 4
		# is now invincible.
		# Toggle god mode until player is humman
		while not res.endswith(" is no more invincible."):
			# Toggle god mode
			res = self._command("godmode", player)
			if res.endswith(" is no more invincible."):
				return True

			# Fail safe
			max_tries -= 1
			if max_tries <= 0:
				return False

	def healAllPlayers(self):
		players = self.onlinePlayers()
		if not players:
			return 0

		count = 0
		for player in players:
			healed = self.healPlayer(player)
			if healed:
				count += 1

		return count

	def giveItemToPlayer(self, player, itemid, count=1):
		if not self._isValid_playerName(player):
			return False
		if not isinstance(count, int) or count < 1 or count > 99:
			return False

		res = self._command("additem", player, itemid, str(count))
		if res == 'Pass username':
			return False
		#Item Base.BaseballBat Added in thanos's inventory.
		elif res.startswith("Item ") and (' Added in ' in res) and res.endswith("'s inventory."):
			return True
		return False

	def options(self):
		res = self._command("showoptions")
		lines = res.split('\n')

		if lines[0] != 'List of Server Options:':
			return False

		# Extract option items from text
		items = [line.strip()[2:].strip() for line in lines[1:] if line.startswith('* ')]

		options = {}
		for item in items:
			pair = item.split('=', 1)
			key = pair[0]
			value = pair[1]
			# Detect type
			if value in ['true', 'false']:
				value = value == 'true'
			elif value.isdigit():
				value = int(value)
			elif value.replace('.','',1).isdigit():
				value = float(value)

			options[key] = value

		return options

	def save(self):
		res = self._command("save")
		if res == 'World saved':
			return True
		return False

	def quit(self):
		res = self._command("quit")
		print(res)



server_ip = '192.168.2.51'
server_port = 27015
server_password = '@dark12321'

if __name__ == "__main__":
	server = ZomboidServer(ip=server_ip, port=server_port, password=server_password)

	## Heal all players
	#healed = server.healAllPlayers()
	#print(f"Healded {healed} players.")

	print(server.onlinePlayers())
	print(server.healAllPlayers())
	#print(server.healPlayer('thanos'))
	#print(server.save())
	print(server.quit())

	#print(server.options())
	#print(server.giveItemToPlayer('thanos', 'Base.BaseballBat', 1))

	#command = pz.serverMsg("You dead yet?")
	#print(command.response)
	#print(pz.serverMsg("Hello!").response)

	#.command("command", "arg1", "arg2", "etc")
	

	#print(pz.command("godmode", "thanos").response)
	#print(pz.command("godmode", "thanos").response)
