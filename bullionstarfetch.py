import httpx
import asyncio
from datetime import date, timedelta 
from bullionstarreply import BullionStarReply

client = httpx.AsyncClient()

async def fetch_bullionstar_spot_price(fromIndex:str="XAG", toIndex:str="EUR", period:str="MAX") -> dict[date, float]:
    url = f"https://services.bullionstar.com/spot-chart/getChart?product=false&productId=0&productTo=false&productIdTo=0&fromIndex={fromIndex}&toIndex={toIndex}&period={period}&width=1000&height=1000&timeZoneId=Europe%2FBrussels&weightUnit=tr_oz"
    resultDict: dict[date, float] = {}
    response = await client.get(url)
    if response.status_code == 200:
        print ("Fetched bullionstar spot price data")
        print (response.json())
        bullionstar_reply = BullionStarReply(**response.json())
        print ("Parsed bullionstar reply:", bullionstar_reply)

        days_diff = (bullionstar_reply.endDate - bullionstar_reply.startDate).days
        print ("days diff: ", days_diff)

        delta_d : int = bullionstar_reply.dataSeries[-1]['d'] - bullionstar_reply.dataSeries[0]['d']
        print ("delta d: ", delta_d)

        
        for dv in bullionstar_reply.dataSeries:
            approx_date = bullionstar_reply.startDate + timedelta(days=dv['d'] // (delta_d // days_diff) )
            print (f" approx date: {approx_date}, value: {dv['v']} ")
            resultDict[approx_date] = dv['v']

    return resultDict

        #return response.json().get("data", [])
    
# https://services.bullionstar.com/spot-chart/getChart?product=false&productId=0&productTo=false&productIdTo=0&fromIndex=XAG&toIndex=EUR&period=MAX&width=1000&height=1000&timeZoneId=Europe%2FBrussels&weightUnit=tr_oz


if __name__ == "__main__":
    asyncio.run(fetch_bullionstar_spot_price())
