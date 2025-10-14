import requests
import uuid
from datetime import date
from requests import Session
from seriesdata import SeriesData
from ucitsfunds import UCITS_FUNDS

def collect_morningstar_maasToken(reqSession:Session, tickerQuery:str="0P0001I3S0") -> str: # just collecting the token
    url = f"https://global.morningstar.com/en-gb/investments/etfs/{tickerQuery}/chart"
    headers = {
        "Accept": "application/json",
        "Origin": "https://global.morningstar.com",
        "Referer": f"https://global.morningstar.com/en-gb/investments/etfs/{tickerQuery}/chart",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0",
        "x-api-requestid": str(uuid.uuid4())
    }

    response = reqSession.get(url, headers=headers)
    json_data = str(response.text)
    if 'maasToken:"' in json_data:
        try:
            return json_data.split('maasToken:"')[1].split('"')[0]
        except Exception:
            raise Exception("maasToken was not found in the response")
    raise Exception("Failed to fetch data")


def fetch_morningstar_history(reqSession:Session, tickerQuery:str, maasBearerToken:str, startDate:str="1900-01-01", endDate:str=date.today().isoformat()) -> list[SeriesData]:
    url = f"https://www.us-api.morningstar.com/QS-markets/chartservice/v2/timeseries?query={tickerQuery}:totalReturn,nav,open,high,low,close,volume,previousClose"
    url += "&frequency=d" # frequency = 1/d : daily, m : monthly
    url += f"&startDate={startDate}&endDate={endDate}"
    url += "&trackMarketData=3.6.5&instid=DOTCOM"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0",
        "Authorization": f"Bearer {maasBearerToken}",
    }
    response = reqSession.get(url, headers=headers)
    if response.status_code == 200:
        return [SeriesData(**item) for item in response.json()[0]["series"]]
    return []


if __name__ == "__main__":
    reqSession = requests.Session()

    maas_token = collect_morningstar_maasToken(reqSession)
    print ("Fetched maas bearer token:", maas_token)

    for fund in UCITS_FUNDS.__dict__.values():
        datas = fetch_morningstar_history(reqSession, fund.morningstarId, maas_token)

        for d in datas:
            print (d)
            # http post request to webAPI to be done here

        print ("\n\n")
    