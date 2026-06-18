from fastapi import APIRouter
import math

router = APIRouter(prefix="/api/v2/finance", tags=["Finance V2"])

@router.get("/emi")
async def emi(principal: float, annual_rate: float, years: int):
    r = annual_rate / 12 / 100
    n = years * 12

    emi = (principal * r * ((1+r)**n)) / (((1+r)**n)-1)

    total_payment = emi * n
    total_interest = total_payment - principal

    return {
        "monthly_emi": round(emi,2),
        "total_interest": round(total_interest,2),
        "total_payment": round(total_payment,2)
    }

@router.get("/sip")
async def sip(monthly_investment: float, annual_return: float, years: int):
    r = annual_return / 12 / 100
    n = years * 12

    fv = monthly_investment * (((1+r)**n - 1)/r) * (1+r)

    invested = monthly_investment * n

    return {
        "invested_amount": round(invested,2),
        "future_value": round(fv,2),
        "profit": round(fv-invested,2)
    }

@router.get("/gst")
async def gst(amount: float, gst_rate: float = 18):
    gst_amount = amount * gst_rate / 100

    return {
        "base_amount": amount,
        "gst_amount": round(gst_amount,2),
        "total_amount": round(amount + gst_amount,2)
    }

@router.get("/fd")
async def fixed_deposit(principal: float, rate: float, years: int):
    maturity = principal * ((1 + rate/100) ** years)

    return {
        "principal": principal,
        "maturity_amount": round(maturity,2),
        "interest_earned": round(maturity-principal,2)
    }

@router.get("/roi")
async def roi(investment: float, return_amount: float):
    profit = return_amount - investment

    roi_percent = (profit/investment)*100

    return {
        "profit": round(profit,2),
        "roi_percent": round(roi_percent,2)
    }

@router.get("/networth")
async def networth(assets: float, liabilities: float):
    return {
        "net_worth": round(assets-liabilities,2)
    }
