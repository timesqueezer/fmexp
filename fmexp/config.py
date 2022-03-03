from datetime import timedelta


SECRET_KEY = 'oomeihu8ia7eHoh6quae4sheen5hie3aixaej8aoju4bohjaet0Ohh7ohdu9Quahbie5duyeequ1Ui8ui7eathoobonoogorooc2rohkoh1goh3moluch9bai0biu9su'

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@/fmexp'
SQLALCHEMY_TRACK_MODIFICATIONS = False

LAYOUT_NAME = 'layout2'

JWT_AUTH_USERNAME_KEY = 'email'
JWT_EXPIRATION_DELTA = timedelta(days=90)
