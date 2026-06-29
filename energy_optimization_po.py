"""
Energy Optimization with Pyomo. Refactored from Navid Shirzadi code based on
his research work.
Project Author Alireza Adli alireza.adli4@gmail.com
demianadli.com
"""

import matplotlib.pyplot as plt
import pyomo.environ as po
from pyomo.opt import SolverFactory
import pandas as pd
import numpy as np
from typing import Dict


def pyomo_energy_optimization(user_input: Dict):
  # Constraints of the model
  def storage_1(model, t):
    if t == 1:
      return model.battery_energy[t] == model.battery_capacity
    else:
      return model.battery_energy[t] == model.battery_energy[t - 1] + \
             model.charging_capacity[t] * model.battery_charging - \
             model.discharging_capacity[t] / model.battery_discharging

  def storage_2(model, t):
    return model.battery_energy[t] >= model.battery_capacity * \
           model.charge_state_min

  def storage_3(model, t):
    return model.battery_energy[t] <= model.battery_capacity

  def storage_4(model, t):
    return model.charging_capacity[t] * model.battery_charging + \
           model.discharging_capacity[t] / model.battery_discharging <= \
           model.charge_discharge_max * model.battery_capacity

  def storage_5(model, t):
    return model.charging_capacity[t] <= \
           model.battery_capacity * model.gamma[t]

  def storage_6(model, t):
    return model.discharging_capacity[t] <= \
           model.battery_capacity * model.teta[t]

  def storage_7(model, t):
    return model.gamma[t] + model.teta[t] == 1

  def grid_1(model, t):
    return model.sold_grid_capacity[t] <= \
           (model.wind_power_surplus[t] + model.pv_power_surplus[t]) * \
           model.electricity_to_grid * model.eta[t]

  def grid_2(model, t):
    return model.purchased_grid_capacity[t] <= model.grid_purchase_max * \
           model.lambdaa[t]

  def grid_3(model, t):
    return model.eta[t] + model.lambdaa[t] == 1

  def wind_surplus(model, t):
    return model.wind_turbines_number * model.wind[t] == \
           (model.wind_used_energy[t] + model.wind_power_surplus[t])

  def pv_surplus(model, t):
    return model.pv_panels_number * model.pv[t] == model.pv_used_power[t] \
           + model.pv_power_surplus[t]

  def balance(model, t):
    return model.wind_used_energy[t] + model.pv_used_power[t] + \
           model.discharging_capacity[t] + model.purchased_grid_capacity[t] + \
           model.loss[t] >= model.Load[t] + model.charging_capacity[t] + \
           model.sold_grid_capacity[t]

  def loss_constraint(model, t):
    return sum(model.loss[t] for t in model.t) <= 0.01 * \
           sum(model.Load[t] for t in model.t)

  def objective_rule(model):
    return model.pv_panels_number * \
           (model.pv_cost + model.dc_dc_converter_cost) * \
           (1 + model.pv_operating_cost / model.capital_recovery_factor) + \
           (model.wind_turbines_number * model.wind_turbine_cost *
            (1 + model.wind_turbine_operating_cost /
             model.capital_recovery_factor)) + \
           model.wind_turbines_number * model.ac_dc_rectifier_cost + \
           model.battery_capacity * (model.battery_kwh_price +
                                     model.dc_ac_inverter_cost) + \
           model.battery_operating_cost * \
           (sum((model.discharging_capacity[t] + model.charging_capacity[t]) /
                model.capital_recovery_factor for t in model.t)) + \
           ((model.battery_maintenance_cost * model.charge_discharge_max *
             model.battery_capacity) +
            (model.battery_replacement_cost * model.battery_capacity)) * \
           model.capital_recovery_factor_battery + \
           sum((model.grid_purchase_price * model.purchased_grid_capacity[t]) /
               model.capital_recovery_factor for t in model.t) - \
           sum((model.grid_selling_price * model.sold_grid_capacity[t]) /
               model.capital_recovery_factor for t in model.t) + \
           sum(model.loss[t] * model.loss_coefficient for t in model.t) + \
           sum(model.purchased_grid_capacity[t] *
               model.nonrenewable_grid_portion *
               model.environmental_coefficient_penalty for t in model.t)

  default_values = dict(building_load=None,
                        battery_charging=0.95, battery_discharging=0.95,
                        charge_discharge_max=0.35, electricity_to_grid=1,
                        pv_cost=1246, dc_dc_converter_cost=100,
                        grid_purchase_max=200000,
                        wind_turbine_operating_cost=0.002,
                        wind_turbine_cost=2077,
                        capital_recovery_factor=0.064,
                        capital_recovery_factor_battery=1.7743,
                        ac_dc_rectifier_cost=100,
                        dc_ac_inverter_cost=100,
                        battery_kwh_price=670,
                        battery_operating_cost=0.00054,
                        battery_maintenance_cost=13.2,
                        battery_replacement_cost=670,
                        grid_purchase_price=0.08, grid_selling_price=0.08,
                        charge_state_min=0.2, loss_coefficient=0.8,
                        pv_operating_cost=0.001,
                        nonrenewable_grid_portion=0,
                        environmental_coefficient_penalty=1,

                        area=5020.0,
                        wind_turbines_number=1200,
                        battery_capacity=None, battery_energy=None,
                        charging_capacity=None,
                        discharging_capacity=None,
                        wind_used_energy=None,
                        wind_power_surplus=None,
                        pv_used_power=None, pv_power_surplus=None,
                        purchased_grid_capacity=2000,
                        sold_grid_capacity=2000, loss=100)

  for each in user_input:
    if user_input[each] is None:
      user_input[each] = default_values[each]

  input_daily_sum = pd.read_excel('data/Input_Daily_Sum.xlsx')
  model = po.ConcreteModel()
  model.t = po.RangeSet(1, 365)

  if user_input['building_load']:
    model.Load = user_input['building_load']
  else:
    model.Load = \
      po.Param(model.t,
               initialize=dict(zip(input_daily_sum.time,
                                   input_daily_sum.Load)))
  model.wind = \
    po.Param(model.t,
             initialize=dict(zip(input_daily_sum.time,
                                 input_daily_sum.Wind)))

  model.pv = \
    po.Param(model.t,
             initialize=dict(zip(input_daily_sum.time,
                                 input_daily_sum.PV)))

  # Parameters of the model
  model.battery_charging = po.Param(
    initialize=user_input['battery_charging'])
  model.battery_discharging = po.Param(
    initialize=user_input['battery_discharging'])
  model.charge_discharge_max = po.Param(
    initialize=user_input['charge_discharge_max'])
  model.electricity_to_grid = po.Param(
    initialize=user_input['electricity_to_grid'])
  model.pv_cost = po.Param(
    initialize=user_input['pv_cost'])
  model.dc_dc_converter_cost = po.Param(
    initialize=user_input['dc_dc_converter_cost'])
  model.grid_purchase_max = po.Param(
    initialize=user_input['grid_purchase_max'])
  model.wind_turbine_cost = po.Param(
    initialize=user_input['wind_turbine_cost'])
  model.wind_turbine_operating_cost = po.Param(
    initialize=user_input['wind_turbine_operating_cost'])
  model.capital_recovery_factor = po.Param(
    initialize=user_input['capital_recovery_factor'])
  model.capital_recovery_factor_battery = po.Param(
    initialize=user_input['capital_recovery_factor_battery'])
  model.ac_dc_rectifier_cost = po.Param(
    initialize=user_input['ac_dc_rectifier_cost'])
  model.dc_ac_inverter_cost = po.Param(
    initialize=user_input['dc_ac_inverter_cost'])
  model.battery_kwh_price = po.Param(
    initialize=user_input['battery_kwh_price'])
  model.battery_operating_cost = po.Param(
    initialize=user_input['battery_operating_cost'])
  model.battery_maintenance_cost = po.Param(
    initialize=user_input['battery_maintenance_cost'])
  model.battery_replacement_cost = po.Param(
    initialize=user_input['battery_replacement_cost'])
  model.grid_purchase_price = po.Param(
    initialize=user_input['grid_purchase_price'])
  model.grid_selling_price = po.Param(
    initialize=user_input['grid_selling_price'])
  model.charge_state_min = po.Param(
    initialize=user_input['charge_state_min'])
  model.loss_coefficient = po.Param(
    initialize=user_input['loss_coefficient'])
  model.pv_operating_cost = po.Param(
    initialize=user_input['pv_operating_cost'])
  model.nonrenewable_grid_portion = po.Param(
    initialize=user_input['nonrenewable_grid_portion'])
  model.environmental_coefficient_penalty = po.Param(
    initialize=user_input['environmental_coefficient_penalty'])

  # Variables of the model
  model.pv_panels_number = po.Var(
    within=po.Integers, bounds=(0, user_input['area'] / 1.32))

  model.wind_turbines_number = po.Var(
    within=po.Integers, bounds=(0, user_input['wind_turbines_number']))
  model.battery_capacity = po.Var(
    bounds=(0, user_input['battery_capacity']))
  model.battery_energy = po.Var(
    model.t, bounds=(0, user_input['battery_energy']))
  model.charging_capacity = po.Var(
    model.t, bounds=(0, user_input['charging_capacity']))
  model.discharging_capacity = po.Var(
    model.t, bounds=(0, user_input['discharging_capacity']))
  model.wind_used_energy = po.Var(
    model.t, bounds=(0, user_input['wind_used_energy']))
  model.wind_power_surplus = po.Var(
    model.t, bounds=(0, user_input['wind_power_surplus']))
  model.pv_used_power = po.Var(
    model.t, bounds=(0, user_input['pv_used_power']))
  model.pv_power_surplus = po.Var(
    model.t, bounds=(0, user_input['pv_power_surplus']))
  model.purchased_grid_capacity = po.Var(
    model.t, bounds=(0, user_input['purchased_grid_capacity']))
  model.sold_grid_capacity = po.Var(
    model.t, bounds=(0, user_input['sold_grid_capacity']))
  model.loss = po.Var(
    model.t, domain=po.NonNegativeReals, bounds=(0, user_input['loss']))
  model.gamma = po.Var(
    model.t, within=po.Binary)
  model.teta = po.Var(
    model.t, within=po.Binary)
  model.lambdaa = po.Var(
    model.t, within=po.Binary)
  model.eta = po.Var(
    model.t, within=po.Binary)

  # Assigning the constraints functions
  model.constraint_1 = po.Constraint(model.t, rule=storage_1)
  model.constraint_2 = po.Constraint(model.t, rule=storage_2)
  model.constraint_3 = po.Constraint(model.t, rule=storage_3)
  model.constraint_4 = po.Constraint(model.t, rule=storage_4)
  model.constraint_5 = po.Constraint(model.t, rule=storage_5)
  model.constraint_6 = po.Constraint(model.t, rule=storage_6)
  model.constraint_7 = po.Constraint(model.t, rule=storage_7)
  model.constraint_8 = po.Constraint(model.t, rule=grid_1)
  model.constraint_9 = po.Constraint(model.t, rule=grid_2)
  model.constraint_10 = po.Constraint(model.t, rule=grid_3)
  model.constraint_11 = po.Constraint(model.t, rule=wind_surplus)
  model.constraint_12 = po.Constraint(model.t, rule=pv_surplus)
  model.constraint_13 = po.Constraint(model.t, rule=balance)
  model.constraint_14 = po.Constraint(model.t, rule=loss_constraint)

  model.objective = po.Objective(rule=objective_rule, sense=po.minimize)

  model.write('data/Opt_New.lp')

  optmization = SolverFactory('scip')
  results = optmization.solve(model, tee=True)

  load_sum = input_daily_sum['Load'].sum()

  object_fu = po.value(model.objective)
  cost_of_energy = po.value(
    model.objective) * model.capital_recovery_factor / load_sum
  number_of_pv = po.value(model.pv_panels_number)
  number_of_wind_turbines = po.value(model.wind_turbines_number)
  battery_storage_capacity = po.value(model.battery_capacity)

  gs_values = pd.DataFrame(list(model.sold_grid_capacity[:].value),
                           columns=['Gs'])
  gp_values = pd.DataFrame(list(model.purchased_grid_capacity[:].value),
                           columns=['Gp'])
  pd_values = pd.DataFrame(list(model.discharging_capacity[:].value),
                           columns=['Pd'])
  pc_values = pd.DataFrame(list(model.charging_capacity[:].value),
                           columns=['Pc'])
  eb_values = pd.DataFrame(list(model.battery_energy[:].value),
                           columns=['Eb'])
  e_wind_values = pd.DataFrame(list(model.wind_used_energy[:].value),
                               columns=['EWind'])
  e_pv_values = pd.DataFrame(list(model.pv_used_power[:].value),
                             columns=['EPV'])
  es_wind_values = pd.DataFrame(list(model.wind_power_surplus[:].value),
                                columns=['ESWind'])
  es_pv_values = pd.DataFrame(list(model.pv_power_surplus[:].value),
                              columns=['ESPV'])
  unmet_load = pd.DataFrame(list(model.loss[:].value),
                            columns=['Loss'])
  indexed_result = pd.concat([gs_values, gp_values, pd_values,
                              pc_values, eb_values, e_wind_values,
                              e_pv_values, es_wind_values,
                              es_pv_values, unmet_load], axis=1)

  total_capital_cost = po.value(model.pv_panels_number) * \
                               (model.pv_cost + model.dc_dc_converter_cost) + \
                               (po.value(model.wind_turbines_number) *
                                model.wind_turbine_cost) + \
                               (po.value(model.battery_capacity) *
                                (model.battery_kwh_price +
                                 model.dc_ac_inverter_cost))

  renewable_penetration = (((np.array(e_pv_values.sum())) +
                            (np.array(e_wind_values.sum())) -
                           (gs_values.sum())) / load_sum).iloc[0]
  benefit = ((np.array(load_sum) + np.array(gs_values.sum()) -
             np.array(gp_values.sum())) * 0.07) - 0.02 * total_capital_cost
  payback_period = np.round(np.array(total_capital_cost)/(benefit * 1.7743))

  indexed_result.to_csv('data/results_local_new.csv')
  results_local_new = pd.read_csv('data/results_local_new.csv')
  plt.plot(results_local_new['Loss'])
  return object_fu, cost_of_energy, number_of_pv, \
      number_of_wind_turbines, battery_storage_capacity, \
      total_capital_cost, renewable_penetration, payback_period[0]
