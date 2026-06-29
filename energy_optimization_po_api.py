"""
API for running Energy Optimization with Pyomo.
Project Author Alireza Adli alireza.adli4@gmail.com
demianadli.com
"""


from flask import send_file, request, make_response, Response, Flask
from flask_apispec import use_kwargs, doc
from flask_restful import Resource, Api
from marshmallow import Schema, fields

from energy_optimization_po import *


class EnergyOptimizationPyomoPostData(Schema):
  building_load = fields.List(
    fields.Float(),
    description='Yearly Load Demand', missing=None)

  battery_charging = fields.Float(
    description='Battery Charging Efficiency', missing=None)
  battery_discharging = fields.Float(
    description='Battery Discharging Efficiency', missing=None)
  charge_discharge_max = fields.Float(
    description='Max Charge Discharge Rate', missing=None)
  electricity_to_grid = fields.Integer(
    description='Electricity\'s portion to sell to grid', missing=None)
  pv_cost = fields.Integer(
    description='PV cost', missing=None)
  dc_dc_converter_cost = fields.Integer(
    description='DC to DC converter cost', missing=None)
  grid_purchase_max = fields.Integer(
    description='Maximum Grid Purchase', missing=None)
  wind_turbine_operating_cost = fields.Float(
    description='Wind Turbine Operating Cost', missing=None)
  wind_turbine_cost = fields.Integer(
    description='Wind Turbine Cost', missing=None)
  capital_recovery_factor = fields.Float(
    description='Capital Recovery Factor', missing=None)
  capital_recovery_factor_battery = fields.Integer(
    description='Capital Recovery Factor of Battery', missing=None)
  ac_dc_rectifier_cost = fields.Integer(
    description='AC to DC Rectifier Cost', missing=None)
  dc_ac_inverter_cost = fields.Float(
    description='DC to AC Inverter Cost', missing=None)
  battery_kwh_price = fields.Integer(
    description='Battery Price per kWh', missing=None)
  battery_operating_cost = fields.Float(
    description='Battery Operating Cost', missing=None)
  battery_maintenance_cost = fields.Float(
    description='Battery Maintenance Cost', missing=None)
  battery_replacement_cost = fields.Integer(
    description='Battery Replacement Cost', missing=None)
  grid_purchase_price = fields.Float(
    description='Gird purchase price', missing=None)
  grid_selling_price = fields.Float(
    description='Grid selling price', missing=None)
  charge_state_min = fields.Float(
    description='Charge of the Battery', missing=None)
  loss_coefficient = fields.Float(
    description='Unmet Load Penalty Coefficient', missing=None)
  pv_operating_cost = fields.Float(
    description='Maintenance of PV Panel', missing=None)
  nonrenewable_grid_portion = fields.Integer(
    description='Nonrenewable portion of the grid', missing=None)
  environmental_coefficient_penalty = fields.Integer(
    description='Environmental Coefficient-Penalty', missing=None)

  wind_turbines_number = fields.Integer(
    description='Wind Turbine Capacity', missing=None)
  battery_capacity = fields.Integer(
    description='Battery Capacity', missing=None)
  battery_energy = fields.Integer(
    description='Battery Energy Level', missing=None)
  charging_capacity = fields.Integer(
    description='Battery Charging Power', missing=None)
  discharging_capacity = fields.Integer(
    description='Battery Discharging Power', missing=None)
  wind_used_energy = fields.Integer(
    description='Wind Used Power', missing=None)
  wind_power_surplus = fields.Integer(
    description='Wind Surplus Power', missing=None)
  pv_used_power = fields.Integer(
    description='PV Used Power', missing=None)
  pv_power_surplus = fields.Integer(
    description='PV Surplus Power', missing=None)
  purchased_grid_capacity = fields.Integer(
    description='Grid Purchase', missing=None)
  sold_grid_capacity = fields.Integer(
    description='Grid Sell', missing=None)
  loss = fields.Integer(
    description='Unmet Load', missing=None)
  area = fields.Float(
    description='Area of the roof', missing=None)


class EnergyOptimizationPyomo(Resource):
  @use_kwargs(EnergyOptimizationPyomoPostData)
  def post(self, **kwargs):
    json_data = request.get_json()
    schema = EnergyOptimizationPyomoPostData()
    errors = schema.validate(json_data)
    if errors:
      return errors, 400
    result = pyomo_energy_optimization(kwargs)
    return {'Object FU': result[0], 'Cost of Energy (COE)': result[1],
            'Number of PV': result[2], 'Number of Wind Turbines': result[3],
            'Battery Storage Capacity': result[4],
            'Total Capital Cost ($)': result[5],
            'Renewable Penetration': result[6],
            'Payback Period': result[7]}, 200


app = Flask(__name__)
api = Api(app)


api.add_resource(EnergyOptimizationPyomo, '/result')

app.run(debug=False)
