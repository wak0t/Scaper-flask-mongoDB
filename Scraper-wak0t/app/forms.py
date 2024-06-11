from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ScraperForm(FlaskForm):
    query = StringField('Query', validators=[DataRequired()])
    min_price = IntegerField('Minimum Price', validators=[NumberRange(min=0)])
    max_price = IntegerField('Maximum Price', validators=[NumberRange(min=0)])
    sort_order = SelectField('Sort Order', choices=[('asc', 'Ascending'), ('desc', 'Descending')])
    free_shipping = BooleanField('Free International Shipping')
    exclude_price_range = BooleanField('Exclude Price Range')
    submit = SubmitField('Scrape')

class FilterForm(FlaskForm):
    min_price = IntegerField('Minimum Price', validators=[NumberRange(min=0)])
    max_price = IntegerField('Maximum Price', validators=[NumberRange(min=0)])
    sort_order = SelectField('Sort Order', choices=[('asc', 'Ascending'), ('desc', 'Descending')])
    submit = SubmitField('Filter')