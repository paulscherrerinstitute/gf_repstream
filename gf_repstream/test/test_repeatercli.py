import sys
sys.path.insert(0, '../')

from cli import SRepeater

srepeater = SRepeater(config_file='./gf_repstream_config.json')
print('starting repeater...')

srepeater.start()

print('finishing repeater...')