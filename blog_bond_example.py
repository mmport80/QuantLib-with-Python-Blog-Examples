
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


#######################################################################
## 1) Global data
## 2) Date setup
## 3) Construct yield term structure
## 4) Setup initial bond
## 5) Calibrate and find spread
## 6) Collate results


from QuantLib import *


#######################################################################
## 1) Global data

#switch to quantlib date object
valuation_date = Date(14,4,2014)
maturity_date = Date(1,9,2041)

payment_frequency = Semiannual

#Global data defaults
day_counter = ActualActual(ActualActual.Bond)
compounding = QuantLib.SimpleThenCompounded	

settlement_days = 0

calendar = UnitedStates()
payment_convention = ModifiedFollowing

face = 100
coupon = 0.06875
market_value = 101.5

# Create a dictionary of yield quotes by tenor
zcQuotes = [	(0.0003, Period(1,Months)),
		(0.0004, Period(3,Months)),		
		(0.0006, Period(6,Months)),
		(0.0010, Period(1,Years)),
		(0.0037, Period(2,Years)),
		(0.0082, Period(3,Years)),
		(0.0161, Period(5,Years)),
		(0.0218, Period(7,Years)),
		(0.0265, Period(10,Years)),
		(0.0323, Period(20,Years)),
		(0.0333, Period(25,Years)),
		(0.0348, Period(30,Years))
	]


#######################################################################
## 2) Date setup
	
#if the date is a hol or wknd I then adjust appropriately (advance method)
valuation_date = calendar.advance(valuation_date,0,Days)


#figure out and set today's date, use advance to change as necessary..
#assume that todaysDate = valuation_date
#todays_date = calendar.advance(valuation_date,0,Days)
Settings.instance().evaluationDate = valuation_date


#######################################################################
## 3) Construct yield term structure

def getTermStructure(valuation_date, zcQuotes, calendar, payment_convention, day_counter):

	fixing_days = 0

	# Create deposit rate helpers
	zcHelpers = [ DepositRateHelper(QuoteHandle(SimpleQuote(r)),
			                tenor, 
					fixing_days,
					calendar, 
					payment_convention,
					True, 
					day_counter)
	      	for (r,tenor) in zcQuotes ]
	
	# Term structure to be used in discounting bond cash flows
	return PiecewiseFlatForward(valuation_date, zcHelpers, day_counter)
	

#######################################################################
## 4) Setup initial bond

def getBond( valuation_date, maturity_date, payment_frequency, calendar, face, coupon, payment_convention, bondDiscountingTermStructure, z_spread = 0):
	
	#move back a year in order to capture all accrued interest
	#may be caught out if there's an irregular coupon payment at beginning
	issue_date = calendar.advance(valuation_date,-1,Years)
	
	#Bond schedule T&Cs
	fixedBondSchedule = Schedule(	issue_date,
	    	                	maturity_date, 
					Period(payment_frequency),
	                     		calendar,
	                     		Unadjusted, 
					Unadjusted,
	                     		DateGeneration.Backward, 
					False)
	#Bond T&Cs
	fixedRateBond = FixedRateBond(	0,
	                       		face,
	                       		fixedBondSchedule,
	                       		[coupon],
	                       	 	bondDiscountingTermStructure.dayCounter(),
	                       		payment_convention,
	                       		100,
					issue_date)

	#Zero spread needs to be a 'quote handle' object whatever that is
	zSpreadQuoteHandle = QuoteHandle( SimpleQuote(z_spread) )

	discountingTermStructure = RelinkableYieldTermStructureHandle()
	discountingTermStructure.linkTo(bondDiscountingTermStructure)	
	
	zSpreadedTermStructure = ZeroSpreadedTermStructure(discountingTermStructure, zSpreadQuoteHandle)

	#Create new relinkable handle for calibrated zero spread
	zSpreadRelinkableHandle = RelinkableYieldTermStructureHandle()

	#Link up
	zSpreadRelinkableHandle.linkTo(zSpreadedTermStructure)
	bondEngine_with_added_zspread = DiscountingBondEngine(zSpreadRelinkableHandle)

	#Set new bond engine
	#Ready for use
	fixedRateBond.setPricingEngine(bondEngine_with_added_zspread)
	
	return fixedRateBond


#######################################################################
## 6) Collate results

def getResults(fixedRateBond, compounding):
	#find yield
	yield_rate = fixedRateBond.bondYield(fixedRateBond.dayCounter(),compounding,fixedRateBond.frequency())
	#convert yield to interest rate object
	y = InterestRate(yield_rate,fixedRateBond.dayCounter(),compounding,fixedRateBond.frequency())

	result_duration			= BondFunctions.duration(fixedRateBond,y)
	result_convexity		= BondFunctions.convexity(fixedRateBond,y)
	result_bps			= BondFunctions.bps(fixedRateBond,y)
	result_basis_pt_value		= BondFunctions.basisPointValue(fixedRateBond,y)
	result_npv			= fixedRateBond.NPV()
	result_yield_value_bp		= BondFunctions.yieldValueBasisPoint(fixedRateBond,y)
	result_yield_to_maturity	= yield_rate

	print "Duration: ",result_duration		
	print "Convexity: ",result_convexity		
	print "Bps: ",result_bps		
	print "Basis Pt Value: ",result_basis_pt_value	
	print "NPV: ",result_npv		
	print "Yield Value Bp: ",result_yield_value_bp	
	print "Yield to Maturity: ",result_yield_to_maturity
	print "Accrued: ",fixedRateBond.accruedAmount() 		


# Handle for the term structure linked to flat forward curve
# I think this is used so that curves can be swapped in and out
# Unsure how to do that yet though
bondDiscountingTermStructure = getTermStructure(valuation_date, zcQuotes, calendar, payment_convention, day_counter)

fixedRateBond = getBond(valuation_date, maturity_date, payment_frequency, calendar, face, coupon, payment_convention, bondDiscountingTermStructure)

#######################################################################
## 5) Calibrate and find spread

z_spread = CashFlows.zSpread(	fixedRateBond.cashflows(),  
				#Assume market value input is quoted clean
				market_value + fixedRateBond.accruedAmount(),
				bondDiscountingTermStructure,
				fixedRateBond.dayCounter(),                                
				compounding,
				fixedRateBond.frequency(),
				True
				)

fixedRateBond = getBond(valuation_date, maturity_date, payment_frequency, calendar, face, coupon, payment_convention, bondDiscountingTermStructure, z_spread)

getResults(fixedRateBond, compounding)

