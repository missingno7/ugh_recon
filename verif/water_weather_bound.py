from closure_support import ROOT
from water_weather_build import OUT,FILES
from water_weather_limits import cbmc
def main():
    folder=OUT/'negative-bound';folder.mkdir(parents=True,exist_ok=True);source=folder/'harness.c'
    source.write_text('#include "'+(ROOT/'native/water_weather.c').as_posix()+'"\nint main(void){WeatherFrameCursor cursor;uint8_t colors[5];weather_frame_begin(&cursor,colors,1);__CPROVER_assert(cursor.colors[4]==colors[4],"actual fifth color copied");return 0;}\n')
    result=cbmc(source,folder,[*FILES,ROOT/'verif/water_weather_bound.py'],unwind=1,timeout=60,extra=['--no-array-field-sensitivity'])
    print(result['result'],result['failures']);assert result['result']=='FAIL' and any('weather_frame_begin' in n and 'unwind' in n for n,_ in result['failures'])
if __name__=='__main__':main()
