import os, sys
import arcpy
import urllib, json
import datetime

#SQLGIS CONNECTION
# connection = "SQLGIS_SDEAdmin_SDE_DATA.sde\\"
connection = "SQLGIS_Admin_SDE_DATA.sde\\"


#GLOBAL VARS
BRIDGE_URL = r"https://apps.ramm.co.nz/GIS/?key=bed3db3c5cf7&SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=bed3db3c5cf7:bridge&SRSNAME=EPSG:2193&outputFormat=json"
BRIDGE_FC = "{0}{1}".format(connection, "SDE_DATA.SDEADMIN.RAMM\\SDE_DATA.SDEADMIN.RAMM_BRIDGE")
BRIDGE_FIELDS = ["bridge_id", "bridge_type", "age", "length_m", "rail_to_rail", "bridge_name", "bridge_no", "SHAPE@", "sync_date"]

TREE_URL = "https://apps.ramm.co.nz/GIS/?key=bed3db3c5cf7&SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=bed3db3c5cf7:trees&SRSNAME=EPSG:2193&outputFormat=json"
TREE_FC = "{0}{1}".format(connection, "SDE_DATA.SDEADMIN.RAMM_TREE")
TREE_FIELDS = ["species", "tree_id", "tree_age", "condition", "overhead_wires" , "SHAPE@", "sync_date"]

COUNTSITE_URL = "https://apps.ramm.co.nz/GIS/?key=bed3db3c5cf7&SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=bed3db3c5cf7:countsite&SRSNAME=EPSG:2193&outputFormat=json"
COUNTSITE_FC = "{0}{1}".format(connection, "SDE_DATA.SDEADMIN.RAMM_COUNTSITE")
COUNTSITE_FIELDS = ["count_site_id", "count_site_desc", "count_site_source", "chgd_on", "SHAPE@", "sync_date"]

RUBBISHBIN_URL = "https://apps.ramm.co.nz/GIS/?key=bed3db3c5cf7&SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=bed3db3c5cf7:rubbishbins&SRSNAME=EPSG:2193&outputFormat=json"
RUBBISHBIN_FC = "{0}{1}".format(connection, "SDE_DATA.SDEADMIN.RAMM_RUBBISHBIN")
RUBBISHBIN_FIELDS = ["bin_type", "asset_owner", "system_id", "location_m", "road_id" , "SHAPE@", "sync_date"]

TRAFFIC_LOADING_URL = "https://apps.ramm.co.nz/GIS/?key=bed3db3c5cf7&SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=bed3db3c5cf7:Traffic_loading&SRSNAME=EPSG:2193&outputFormat=json"
TRAFFIC_LOADING_FC = "{0}{1}".format(connection, "SDE_DATA.SDEADMIN.RAMM_TRAFFIC_LOADING")
TRAFFIC_LOADING_FIELDS = ['road_name', 'road_id', 'location', 'latest', 'count_date', 'direction', 'peaktraffic','peak_hour', 'adt', 'pccar', 'pdcv','pcmcv','pchcvi','pchcvii', "SHAPE@", 'sync_date']

POLE_URL = "https://apps.ramm.co.nz/GIS/?key=bed3db3c5cf7&SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=bed3db3c5cf7:pole&SRSNAME=EPSG:2193&outputFormat=json"
POLE_FC = "{0}{1}".format(connection, "SDE_DATA.SDEADMIN.RAMM_POLE")
POLE_FIELDS = ['p_id','pole_make','vertical_distance', 'max_base_dim', 'br_id', 'bracket_type', 'light_make', 'light_model', 'lamp_make', 'lamp_model', "SHAPE@", 'sync_date']

CYCLESTAND_URL = "https://apps.ramm.co.nz/GIS/?key=bed3db3c5cf7&SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=bed3db3c5cf7:cyclestand&SRSNAME=EPSG:2193&outputFormat=json"
CYCLESTAND_FC = "{0}{1}".format(connection, "SDE_DATA.SDEADMIN.RAMM_CYCLESTAND")
CYCLESTAND_FIELDS = ['capacity', 'stand_type', 'system_id', 'location_m', 'road_id', "SHAPE@", 'sync_date']


#OTHER VARS
today = datetime.datetime.now()


def delete_all(fc):
    arcpy.DeleteFeatures_management(fc)

def read_ramm(url):
    """ The function to read url data and return as a dictionary"""
    response = urllib.urlopen(url)

    #writing the response to a dict
    data = json.loads(response.read())
    featList = data["features"]

    #### TREE VALIDATION
    #for feat in featList:
    #    print feat['geometry']['type']
    #    print feat['geometry']['coordinates']
    #    print feat['properties']['species']


    print("json lookup function returned")
    return featList


def ramm_bridge(fields, featList, fc):
    """The function to write the data to SDE"""
    sr = arcpy.SpatialReference(2193)
    cursor = arcpy.da.InsertCursor(fc, fields)
    for feat in featList:
        #find the geometry type
        if feat['geometry']['type'] == "Polygon":
            #print "Polygon"
            array = arcpy.Array()
            for coordinates in feat['geometry']['coordinates']:
                #print coordinates
                for vertex in range(len(coordinates)):
                    array.add(arcpy.Point(coordinates[vertex][0], coordinates[vertex][1]))
                    #print coordinates[vertex]

            geom = arcpy.Polygon(array, sr)

        else:
            print "failed validation"
            break


        #print feat['properties']['bridge_id']
        cursor.insertRow((feat['properties']['bridge_id'],
                          feat['properties']['bridge_type'],
                          feat['properties']['age'],
                          feat['properties']['length_m'],
                          feat['properties']['rail_to_rail'],
                          feat['properties']['bridge_name'],
                          feat['properties']['bridge_no'],
                          geom,
                          today))
    #Delete cursor object
    del cursor
    print"completed bridge"



def ramm_tree(fields, featList, fc):
    """The function to write the data to SDE"""
    sr = arcpy.SpatialReference(2193)
    cursor = arcpy.da.InsertCursor(fc, fields)
    for feat in featList:
        #find the geometry type
        if feat['geometry']['type'] == "Point":
            #print "Point" #for debug
            geom = arcpy.Point(feat['geometry']['coordinates'][0], feat['geometry']['coordinates'][1])
        #print feat['properties']['species']
        cursor.insertRow((feat['properties']['species'],
                          feat['properties']['tree_id'],
                          feat['properties']['tree_age'],
                          feat['properties']['condition'],
                          feat['properties']['overhead_wires'],
                          geom,
                          today))
    #Delete cursor object
    del cursor
    print"completed tree"


def ramm_countsite(fields, featList, fc):
    """The function to write the data to SDE"""
    sr = arcpy.SpatialReference(2193)
    cursor = arcpy.da.InsertCursor(fc, fields)
    for feat in featList:
        #find the geometry type
        if feat['geometry']['type'] == "Point":
            #print "Point" #for debug
            geom = arcpy.Point(feat['geometry']['coordinates'][0], feat['geometry']['coordinates'][1])
        #print feat['properties']['species']
        cursor.insertRow((feat['properties']['count_site_id'],
                          feat['properties']['count_site_desc'][0:500],
                          feat['properties']['count_site_source'],
                          feat['properties']['chgd_on'],
                          geom,
                          today))

    #Delete cursor object
    del cursor
    print"completed countsite"


def ramm_rubbishbin(fields, featList, fc):
    """The function to write the data to SDE"""
    sr = arcpy.SpatialReference(2193)
    cursor = arcpy.da.InsertCursor(fc, fields)
    for feat in featList:
        #find the geometry type
        if feat['geometry']['type'] == "Point":
            #print "Point" #for debug
            geom = arcpy.Point(feat['geometry']['coordinates'][0], feat['geometry']['coordinates'][1])
        #print feat['properties']['species']
        cursor.insertRow((feat['properties']['bin_type'],
                          feat['properties']['asset_owner'],
                          feat['properties']['system_id'],
                          feat['properties']['location_m'],
                          feat['properties']['road_id'],
                          geom,
                          today))

    #Delete cursor object
    del cursor
    print"completed rubbishbin"


def ramm_traffic_loading(fields, featList, fc):
    """The function to write the data to SDE"""
    sr = arcpy.SpatialReference(2193)
    cursor = arcpy.da.InsertCursor(fc, fields)
    for feat in featList:
        #find the geometry type
        if feat['geometry']['type'] == "Point":
            #print "Point" #for debug
            geom = arcpy.Point(feat['geometry']['coordinates'][0], feat['geometry']['coordinates'][1])
        #print feat['properties']['species']
        cursor.insertRow((feat['properties']['road_name'],
                          feat['properties']['road_id'],
                          feat['properties']['location'],
                          feat['properties']['latest'],
                          feat['properties']['count_date'],
                          feat['properties']['direction'],
                          feat['properties']['peaktraffic'],
                          feat['properties']['peak_hour'],
                          feat['properties']['adt'],
                          feat['properties']['pccar'],
                          feat['properties']['pclcv'],
                          feat['properties']['pcmcv'],
                          feat['properties']['pchcvi'],
                          feat['properties']['pchcvii'],
                          #feat['properties']['notes'][0:50],
                          geom,
                          today))

    #Delete cursor object
    del cursor
    print"completed rubbishbin"


def ramm_pole(fields, featList, fc):
    """The function to write the data to SDE"""
    sr = arcpy.SpatialReference(2193)
    cursor = arcpy.da.InsertCursor(fc, fields)
    for feat in featList:
        #find the geometry type
        if feat['geometry']['type'] == "Point":
            #print "Point" #for debug
            geom = arcpy.Point(feat['geometry']['coordinates'][0], feat['geometry']['coordinates'][1])
        #print feat['properties']['species']
        cursor.insertRow((feat['properties']['p_id'],
                          feat['properties']['pole_make'],
                          feat['properties']['vertical_distance'],
                          feat['properties']['max_base_dim'],
                          feat['properties']['br_id'],
                          feat['properties']['bracket_type'],
                          feat['properties']['light_make'],
                          feat['properties']['light_model'],
                          feat['properties']['lamp_make'],
                          feat['properties']['lamp_model'],
                          geom,
                          today))

    #Delete cursor object
    del cursor
    print"completed pole"


def ramm_cyclestand(fields, featList, fc):
    """The function to write the data to SDE"""
    sr = arcpy.SpatialReference(2193)
    cursor = arcpy.da.InsertCursor(fc, fields)
    for feat in featList:
        #find the geometry type
        if feat['geometry']['type'] == "Point":
            #print "Point" #for debug
            geom = arcpy.Point(feat['geometry']['coordinates'][0], feat['geometry']['coordinates'][1])
        #print feat['properties']['species']
        cursor.insertRow((feat['properties']['capacity'],
                          feat['properties']['stand_type'],
                          feat['properties']['system_id'],
                          feat['properties']['location_m'],
                          feat['properties']['road_id'],
                          geom,
                          today))

    #Delete cursor object
    del cursor
    print"completed cyclestand"


#### BRIDGES ####
delete_all(BRIDGE_FC)
featList = read_ramm(BRIDGE_URL)
ramm_bridge(BRIDGE_FIELDS, featList, BRIDGE_FC)

#### TREE ####
delete_all(TREE_FC)
featList = read_ramm(TREE_URL)
ramm_tree(TREE_FIELDS, featList, TREE_FC)

#### COUNTSITES ####
delete_all(COUNTSITE_FC)
featList = read_ramm(COUNTSITE_URL)
ramm_countsite(COUNTSITE_FIELDS, featList, COUNTSITE_FC)

#### RUBBISHBINS ####
delete_all(RUBBISHBIN_FC)
featList = read_ramm(RUBBISHBIN_URL)
ramm_rubbishbin(RUBBISHBIN_FIELDS, featList, RUBBISHBIN_FC)

#### TRAFFIC LOADING ####
delete_all(TRAFFIC_LOADING_FC)
featList = read_ramm(TRAFFIC_LOADING_URL)
ramm_traffic_loading(TRAFFIC_LOADING_FIELDS, featList, TRAFFIC_LOADING_FC)

#### POLE ####
delete_all(POLE_FC)
featList = read_ramm(POLE_URL)
ramm_pole(POLE_FIELDS, featList, POLE_FC)

#### CYCLESTAND ####
delete_all(CYCLESTAND_FC)
featList = read_ramm(CYCLESTAND_URL)
ramm_cyclestand(CYCLESTAND_FIELDS, featList, CYCLESTAND_FC)


print ("welldone")
