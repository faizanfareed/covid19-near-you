
$(document).ready(function () {





    function LocatePostion_AndDrawRangeCircle(current_latitude, current_longitude) {

        var green = {
            radius: FirstRangeCircleRadius,
            fillColor: "#5c6bc0",
            color: "#ffffff",
            weight: 2,
            opacity: 0.1,
            fillOpacity: 0.4
        };

        var yellow = {
            radius: SecondRangeCircleRadius,
            fillColor: "#7986cb",
            color: "#ffffff",
            weight: 2,
            opacity: 0.0,
            fillOpacity: 0.4
        };

        var red = {
            radius: ThirdRangeCircleRadius,
            fillColor: "#9fa8da",
            color: "#ffffff",
            weight: 2,
            opacity: 0.0,
            fillOpacity: 0.2
        };


        FirstRangeCircle = L.circle([current_latitude, current_longitude], green).addTo(map);

        SecondRangeCircle = L.circle([current_latitude, current_longitude], yellow).addTo(map);

        ThirdRangeCircle = L.circle([current_latitude, current_longitude], red).addTo(map);


        CurrentLocationMarker = L.marker([current_latitude, current_longitude]).addTo(map);

        map.flyTo([current_latitude, current_longitude], 12);


    }

    function UnlocatePostion_AndRemoveRangeCircle() {

        if (FirstRangeCircle != undefined && SecondRangeCircle != undefined && ThirdRangeCircle != undefined) {
            // console.log('Removed marker is called')
            FirstRangeCircle.remove(); SecondRangeCircle.remove(); ThirdRangeCircle.remove();
            CurrentLocationMarker.remove();

        };

    }


    function validate_latitudeLongitude() {

        var Latitude = $("#id_latitude").val();
        var Longitude = $("#id_longitude").val();

        $(".latitudeerror").remove();
        $(".longitudeerror").remove();

        is_latValid = false;
        is_longValid = false;


        if ($.isNumeric(Latitude)) {
            if (Latitude < REGION_BOUNDRY_MIN_LATITUDE || Latitude >= REGION_BOUNDRY_MAX_LATITUDE) {


                $('#id_latitude').after('<div class="ui pointing red basic left  label latitudeerror" >Latitude out of range</div>');
            } else {
                is_latValid = true
            }

        } else {
            $('#id_latitude').after('<div class="ui pointing red basic left  label latitudeerror" >Must be numeric</div>');

        }

        if ($.isNumeric(Longitude)) {

            if (Longitude < REGION_BOUNDRY_MIN_LONGITUDE || Longitude >= REGION_BOUNDRY_MAX_LONGITUDE) {


                $('#id_longitude').after('<div class="ui pointing red basic left  label longitudeerror" id="error">Longitude out of range</div>');
            } else {
                is_longValid = true
            }

        } else {
            $('#id_longitude').after('<div class="ui pointing red basic left  label longitudeerror" id="error">Must be numeric</div>');

        }

        if (is_latValid && is_longValid) {

            return true;
        } else {


            return false;
        }

    }

    $('#latlongform').on('submit', function (event) {
        event.preventDefault();

        if (validate_latitudeLongitude()) {


            find_nearest_location_ajax();
        }
    });


    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    // AJAX 
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function find_nearest_location_ajax() {


        var csrftoken = getCookie('csrftoken');
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        $.ajax({
            url: endpoint,
            type: "POST",

            data: $("#latlongform").serialize(), // data sent with the post request

            // handle a successful response
            success: function (json) {


                if (json['is_success'] == true) {

                    $('#datablock').empty();
                    $('#datablock').append(json['data']);

                    map.flyTo([json['current_latitude'], json['current_longitude']], 14)

                    UnlocatePostion_AndRemoveRangeCircle();
                    LocatePostion_AndDrawRangeCircle(json['current_latitude'], json['current_longitude'])

                } else {

                    if (json['latitude_error']) {

                        $('#id_latitude').after('<div class="ui pointing red basic left  label latitudeerror" id="error">' + json['latitude_error'] + '</div>');
                    }

                    if (json['longitude_error']) {

                        $('#id_longitude').after('<div class="ui pointing red basic left  label longitudeerror" id="error">' + json['longitude_error'] + '</div>');
                    }
                }



            },

            // handle a non-successful response
            error: function (xhr, errmsg, err) {


                if (xhr.status === 500) {



                    $("#wentworng").remove();

                    $("#error").append("<h3 id='wentworng' class='header ui red'>500 Internal server error.</h3>");

                } else {

                    $("#error").append("<h3 id='wentworng' class='header ui red'>Oops! We have encountered an error.</h3>");

                }
            }
        });
    };




    var datapoints_geojson = new L.geoJson();
    datapoints_geojson.addTo(map);



    function Fetch_PlotGeoJsonData() {


        $.ajax({

            dataType: "json",

            url: url,
            success: function (data) {


                function onEachFeature(feature, layer) {



                    if (feature.properties && feature.properties.name) {
                        var locationtype = 'Location ';

                        if (feature.properties.is_quarantine == 1) {

                            locationtype = ' Quarantine  ' + locationtype;
                            layer.bindPopup('<p><strong>' + locationtype + ' : </strong>' + feature.properties.name + '</p>'

                                + '<p><strong>Created at : </strong>' + feature.properties.created_at + '</p>'
                            ).openPopup();
                        } else {


                            layer.bindPopup('<p><strong>' + locationtype + ' : </strong>' + feature.properties.name + '</p>'

                            ).openPopup();
                        }



                    }

                }


                var Covid19ConfirmedCaseIcon = L.divIcon({

                    className: 'circle',
                    html: '<div class="ringring"></div>'

                    , iconSize: [22, 22]

                });

                var Covid19QuarantineIcon = L.divIcon({

                    className: 'circle',
                    html: '<div class="quarantineringring"></div>'

                    , iconSize: [22, 22]

                });


                L.geoJson(data, {
                    onEachFeature: onEachFeature, pointToLayer: function (feature, latlng) {


                        switch (feature.properties.is_quarantine) {
                            case 1:
                                return L.marker(latlng, { icon: Covid19QuarantineIcon });
                            case 0:
                                return L.marker(latlng, { icon: Covid19ConfirmedCaseIcon });
                        }
                    }
                }).addTo(map);



            }

        });

    }


    Fetch_PlotGeoJsonData();
});