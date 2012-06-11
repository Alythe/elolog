from textfield import TextField, ShortTextField
from numberfield import NumberField, EloField
from championfield import ChampionField

FIELD_TYPES = {
  0: NumberField,
  1: EloField,
  2: TextField,
  3: ShortTextField,
  4: ChampionField,
}

class FieldTypes:
  NUMBER      = 0
  ELO         = 1
  TEXT        = 2
  SHORT_TEXT  = 3
  CHAMPION    = 4

FIELD_TYPE_CHOICES = (
  (FieldTypes.NUMBER, 'Number'),
  (FieldTypes.ELO, 'Elo'),
  (FieldTypes.TEXT, 'Text'),
  (FieldTypes.SHORT_TEXT, 'Short Text'),
  (FieldTypes.CHAMPION, 'Champion'),
)
