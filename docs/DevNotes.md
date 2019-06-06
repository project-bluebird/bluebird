
# Development Notes

General notes on developing with BlueSky / Flask etc.

## BlueSky git submodule

- Should only need updated when the file `bluesky/network/client.py` changes

## BlueSky 'SIMINFO' data

```
Sim speed
Sim DT
Sim time (seconds elapsed)
Sim time (UTC timestamp)
Number of aircraft
Current scenario name
```


## BlueSky 'ACINFO' data

```
data['simt']        = bs.sim.simt   # Sim time

data['id']          = bs.traf.id
data['lat']         = bs.traf.lat
data['lon']         = bs.traf.lon
data['alt']         = bs.traf.alt
data['tas']         = bs.traf.tas
data['cas']         = bs.traf.cas
data['gs']          = bs.traf.gs
data['inconf']      = bs.traf.asas.inconf
data['tcpamax']     = bs.traf.asas.tcpamax
data['nconf_cur']   = len(bs.traf.asas.confpairs_unique)
data['nconf_tot']   = len(bs.traf.asas.confpairs_all)
data['nlos_cur']    = len(bs.traf.asas.lospairs_unique)
data['nlos_tot']    = len(bs.traf.asas.lospairs_all)
data['trk']         = bs.traf.trk
data['vs']          = bs.traf.vs
data['vmin']        = bs.traf.asas.vmin
data['vmax']        = bs.traf.asas.vmax

# Aircrfaft trails
data['swtrails']  = bs.traf.trails.active
data['traillat0'] = bs.traf.trails.newlat0
data['traillon0'] = bs.traf.trails.newlon0
data['traillat1'] = bs.traf.trails.newlat1
data['traillon1'] = bs.traf.trails.newlon1
data['traillastlat']   = bs.traf.trails.lastlat
data['traillastlon']   = bs.traf.trails.lastlon

# Transition level as defined in traf
data['translvl']   = bs.traf.translvl

# ASAS resolutions for visualization
data['asasn']  = bs.traf.asas.asasn
data['asase']  = bs.traf.asas.asase
```
## BlueSky 'ROUTEDATA' data

```
data['acid']    = self.route_acid
data['iactwp']  = route.iactwp
data['aclat']   = bs.traf.lat[idx]
data['aclon']   = bs.traf.lon[idx]
data['wplat']   = route.wplat
data['wplon']   = route.wplon
data['wpalt']   = route.wpalt
data['wpspd']   = route.wpspd
data['wpname']  = route.wpname
```
    
   
