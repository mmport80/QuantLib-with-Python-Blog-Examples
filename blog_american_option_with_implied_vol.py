'''
    QuantLib with Python example
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
valuation_date = Date(17,4,2014) 
expiry_date = Date(15,1,2016)

#terms and conditions
strike_price = 35
put_or_call = Option.Call

#market data
interest_rate = 0.01
#see idivs.org for expected dividend yields
dividend_rate = 0.02
volatility_rate = 0.5 
underlying_price = SimpleQuote(36.35)

market_value = 7.5


def getProcess(valuation_date, interest_rate, dividend_rate, volatility_rate, underlying_price):


	###################################################
	##2)
	#Date setup
	###################################################

	#Assumptions
	calendar = UnitedStates()
	day_counter = ActualActual()

	Settings.instance().evaluation_date = valuation_date


	###################################################
	##3)
	#Curve setup
	###################################################

	interest_curve = FlatForward(valuation_date, interest_rate, day_counter )

	dividend_curve = FlatForward(valuation_date, dividend_rate, day_counter )

	volatility_curve = BlackConstantVol(valuation_date, calendar, volatility_rate, day_counter )

	#Collate market data together
	u = QuoteHandle(underlying_price) 
	d = YieldTermStructureHandle(dividend_curve)
	r = YieldTermStructureHandle(interest_curve)
	v = BlackVolTermStructureHandle(volatility_curve)  
	
	return BlackScholesMertonProcess(u, d, r, v)

	
###################################################
##4)
#Option setup
###################################################

def getAmericanOption(valuation_date, expiry_date, put_or_call, strike_price, process):
	
	exercise = AmericanExercise(valuation_date, expiry_date)
	
	payoff = PlainVanillaPayoff(put_or_call, strike_price)

	#Option Setup
	option =  VanillaOption(payoff, exercise)
	
	time_steps = 100
	grid_points = 100
	
	engine = FDAmericanEngine(process,time_steps,grid_points)
	
	option.setPricingEngine(engine)
	
	return option


###################################################
##5)
##Collate results
###################################################

def getAmericanResults(option):
	print "NPV: ", option.NPV()
	print "Delta: ", option.delta() 
	print "Gamma: ", option.gamma()
	#print "Theta: ", option.theta()

process = getProcess( valuation_date, interest_rate, dividend_rate, volatility_rate, underlying_price)

option = getAmericanOption( valuation_date, expiry_date, put_or_call, strike_price, process)

implied_volatility_rate = option.impliedVolatility(market_value, process)

calibrated_process = getProcess( valuation_date, interest_rate, dividend_rate, implied_volatility_rate, underlying_price)

calibrated_option = getAmericanOption( valuation_date, expiry_date, put_or_call, strike_price, calibrated_process)

#getAmericanResults(calibrated_option)

print "Implied Volatility: ", implied_volatility_rate
print "NPV: ", option.NPV()
print "Delta: ", option.delta() 
print "Gamma: ", option.gamma()



