from textfield import TextField, ShortTextField
from kdafield import KDAField
from numberfield import NumberField, EloField
from championfield import ChampionField, SmallChampionField
from datefield import DateField
from urlfield import URLField

FIELD_TYPES = {
  0: NumberField,
  1: EloField,
  2: TextField,
  3: ShortTextField,
  4: ChampionField,
  5: KDAField,
  6: SmallChampionField,
  7: URLField,
  8: DateField,
}

class FieldTypes:
  NUMBER          = 0
  ELO             = 1
  TEXT            = 2
  SHORT_TEXT      = 3
  CHAMPION        = 4
  KDA             = 5
  SMALL_CHAMPION  = 6
  URL             = 7
  DATE            = 8

FIELD_TYPE_CHOICES = (
  (FieldTypes.NUMBER, 'Number'),
  (FieldTypes.ELO, 'Elo'),
  (FieldTypes.TEXT, 'Text'),
  (FieldTypes.SHORT_TEXT, 'Short Text'),
  (FieldTypes.CHAMPION, 'Champion'),
  (FieldTypes.KDA, 'KDA'),
  (FieldTypes.SMALL_CHAMPION, 'Champion (Small)'),
  (FieldTypes.URL, 'URL'),
  (FieldTypes.DATE, 'Date'),
)
