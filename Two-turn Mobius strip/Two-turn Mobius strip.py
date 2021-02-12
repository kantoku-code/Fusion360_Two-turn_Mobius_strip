#Author-kantoku
#Description-Two-turn Mobius strip
#Fusion360API Python

import adsk.core
import traceback

try:
    from . import config
    from .apper import apper

    from .commands.MobiusStripCore import MobiusStripCore
    from .commands.ktkLanguageMessage import LangMsg

    msgDict = {
        'Two-turn Mobius strip' : '2回転メビウスの帯',
        'Create a Two-turn Mobius strip' : '2回転メビウスの帯を作成'
    }
    lm = LangMsg(msgDict, adsk.core.UserLanguages.JapaneseLanguage)

    # Create our addin definition object
    my_addin = apper.FusionApp(config.app_name, config.company_name, False)
    my_addin.root_path = config.app_path

    my_addin.add_command(
        lm.sLng('Two-turn Mobius strip'),
        MobiusStripCore,
        {
            'cmd_description': lm.sLng('Create a Two-turn Mobius strip'),
            'cmd_id': 'two-turn_Mobius_strip',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'SolidCreatePanel',
            'cmd_resources': 'TwoTurnMobiusStrip',
            'command_visible': True,
            'command_promoted': False,
            'create_feature': False,
        }
    )

except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization: {}'.format(traceback.format_exc()))


def run(context):
    my_addin.run_app()


def stop(context):
    my_addin.stop_app()
