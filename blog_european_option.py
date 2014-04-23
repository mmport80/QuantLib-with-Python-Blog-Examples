'''
    QuantLib with python example
    Copyright (C) 2014 John Orford

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''



from QuantLib import *


###################################################
##1)
##Inputs
###################################################

#dates
valuation_date = Date(13,1,2014) 
expiry_date = Date(13,1,2015)

#terms and conditions
strike_price = 123
put_or_call = Option.Call

#market data
interest_rate = 0.01
#see idivs.org for expected dividend yields
dividend_rate = 0.02
volatility_rate = 0.03 
underlying_price = SimpleQuote(123)


###################################################
##2)
#Date setup
###################################################
Settings.instance().evaluation_date = valuation_date

#Asumptions
calendar = UnitedStates()
day_counter = ActualActual()


###################################################
##3)
#Curve setup
###################################################
interest_curve = FlatForward(valuation_date, interest_rate, day_counter )

dividend_curve = FlatForward(valuation_date, dividend_rate, day_counter )

volatility_curve = BlackConstantVol(valuation_date, calendar, volatility_rate, day_counter )


###################################################
##4)
#Option setup
###################################################
exercise = EuropeanExercise(expiry_date)  
payoff = PlainVanillaPayoff(put_or_call, strike_price)

#Option Setup
option = VanillaOption(payoff, exercise)

#Collate market data together
u = QuoteHandle(underlying_price) 
d = YieldTermStructureHandle(dividend_curve)
r = YieldTermStructureHandle(interest_curve)
v = BlackVolTermStructureHandle(volatility_curve)  
process = BlackScholesMertonProcess(u, d, r, v)

#Set pricing engine
engine = AnalyticEuropeanEngine(process)
option.setPricingEngine(engine)


###################################################
##5)
##Collate results
###################################################
print "NPV: ", option.NPV()
print "Delta: ", option.delta() 
print "Gamma: ", option.gamma()
print "Vega: ", option.vega()
print "Theta: ", option.theta() 
print "Rho: ", option.rho()
print "Dividend Rho: ", option.dividendRho()
print "Theta per Day: ", option.thetaPerDay()
print "Strike Sensitivity: ", option.strikeSensitivity()