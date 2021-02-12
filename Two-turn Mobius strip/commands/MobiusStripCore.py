#Author-kantoku
#Description-Two-turn Mobius strip
#Fusion360API Python

import adsk.core
import adsk.fusion

from ..apper import apper
from .. import config
from .ktkCmdInputHelper import SelectionCommandInputHelper, IntegerSpinnerCommandInputHelper
from .ktkCmdInputHelper import TextBoxCommandInputHelper, ValueCommandInputHelper
from .MobiusStripFactry import MobiusStripFactry
from .ktkLanguageMessage import LangMsg

msgDict = {
    'Center Point' : '中心点',
    'Select Sketch Point' : 'スケッチ点を選択',
    'Twist Count' : 'ねじる回数',
    'Hole Count' : '穴の数',
    'Thickness' : '厚さ',
    'Information' : '情報',
    'is out of scope!' : 'が範囲外です!',
    'is an odd number only!' : 'は奇数のみです!',
    'should be a positive value!' : '0以上にして下さい!'
}

lm = LangMsg(msgDict, adsk.core.UserLanguages.JapaneseLanguage)

_point = SelectionCommandInputHelper(
    'pointIpt',
    lm.sLng('Center Point'),
    lm.sLng('Select Sketch Point'),
    ['SketchPoints'])

_twist = IntegerSpinnerCommandInputHelper(
    'twistIpt',
    lm.sLng('Twist Count'),
    1,
    29,
    2,
    1)

_hole = IntegerSpinnerCommandInputHelper(
    'holeIpt',
    lm.sLng('Hole Count'),
    13,
    49,
    2,
    13)

_thick = ValueCommandInputHelper(
    'thickIpt',
    lm.sLng('Thickness'))

_info = TextBoxCommandInputHelper(
    'infoTxt',
    lm.sLng('Information'),
    '',
    10,
    True)

class MobiusStripCore(apper.Fusion360CommandBase):

    def on_preview(self, command, inputs, args, input_values):
        global _point, _twist, _hole, _thick

        checkLst = [
            _twist.isRange(),
            _twist.isOdd(),
            _hole.isRange(),
            _hole.isOdd()
        ]

        if not all(checkLst):
            return

        MobiusStripFactry.previewMobiusStrip(
            _point.obj.selection(0).entity,
            _twist.obj.value,
            _hole.obj.value
        )

    def on_destroy(self, command, inputs, reason, input_values):
        pass

    def on_input_changed(self, command, inputs, changed_input, input_values):
        global _point, _twist, _hole, _thick, _info

        msg = []

        if not _twist.isRange():
            msg.append(f'{_twist.name} ' + lm.sLng('is out of scope!') + 
                f'({_twist.obj.minimumValue} - {_twist.obj.maximumValue})')

        if not _twist.isOdd():
            msg.append(f'{_twist.name} ' + lm.sLng('is an odd number only!'))


        if not _hole.isRange():
            msg.append(f'{_hole.name} ' + lm.sLng('is out of scope!') + 
                f'({_hole.obj.minimumValue} - {_hole.obj.maximumValue})')

        if not _hole.isOdd():
            msg.append(f'{_hole.name} ' + lm.sLng('is an odd number only!'))


        if not (_thick.obj.value > 0):
            msg.append(f'{_thick.name} ' + lm.sLng('should be a positive value!'))


        if len(msg) > 0:
            _info.obj.text = '\n'.join(msg)
        else:
            _info.obj.text = ''


        command.doExecutePreview()

    def on_execute(self, command, inputs, args, input_values):
        global _point, _twist, _hole, _thick
        thick = _thick.obj.value * 0.5
        MobiusStripFactry.createMobiusStrip(
            _point.obj.selection(0).entity,
            _twist.obj.value,
            _hole.obj.value,
            thick
        )

        _twist.initialValue =  _twist.obj.value
        _hole.initialValue = _hole.obj.value
        _thick.initialValue = adsk.core.ValueInput.createByString(_thick.obj.expression)

    def on_create(self, command, inputs):
        global _point, _twist, _hole, _thick, _info
        _point.register(inputs)
        _twist.register(inputs)
        _hole.register(inputs)
        _thick.register(inputs)
        _info.register(inputs)

    # expansions
    def on_validate(self, command, inputs, args, input_values):
        global _point, _twist, _hole, _thick, _info

        checkLst = [
            _twist.isOdd(),
            _hole.isOdd(),
            _thick.obj.value > 0
        ]

        if all(checkLst):
            args.areInputsValid = True
        else:
            args.areInputsValid = False

    # expansion
    def on_preselect(self, command, inputs, args, pre_input, input_values):
        pass