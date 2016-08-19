
/*
 * Retrieve the race results from the REST GET endpoint provided and use them
 * to populate a bootstrap-table on the page.
 *
 * Arguements:
 *  restURL: string url for the endpoint to hit http://127.0.0.1:8000/api/TrackName/1/SingleRaceDetails/125/
 *  singleRaceDetailID: id/pk for the SingleRaceDetails model, this is used to identify the id of the
 *      header and the table we are going to populate.
 *
 * Example html:
 *       <div id="span-new-race-{{ singleracedetail.id }}"></div>
 *       <table id="table-new-race-{{ singleracedetail.id }}"></table>
 *
 */
var populateSingleRaceFromRestEndpoint = function(restURL, singleRaceDetailID) {
  $.ajax({
    // Example - http://127.0.0.1:8000/api/TrackName/1/SingleRaceDetails/125/
    url: restURL,
    contentType:"application/json; charset=utf-8",
    dataType: "json",
    type: "GET"
  }).error(function(r){
    console.log(r);
  }).success(function(r){
    //console.log("success", r);
    var racedate = moment(r.racedate);
    var formatedRace = "";
    racedate.local();
    // Reference - http://momentjs.com/docs/#/displaying/
    formatedDate = racedate.format("dddd MMM Do YYYY h:mm a");

    var header = r.racedata + " " + r.maineventparsed + " Rnd:" + r.roundnumber + " Race:" + r.racenumber + " </br>" + formatedDate;
    $("#span-new-race-" + singleRaceDetailID).html(header);

    var raceresults = r.raceresults;

    // We want to clean up the times.
    racedata = _.map(raceresults, function(race) {
      // We want to trim off the zeros, example: "06:17.251000"
      if (race.racetime){
        // only trim first char if its zero.
        if (race.racetime[0] = '0'){
          race.racetime =  race.racetime.substring(1, race.racetime.length-1);
        }
        race.racetime =  race.racetime.substring(0, (race.racetime.length-1-2));
      }
      return race;
    });

    //console.log("Data for the graph:", racedata);
    $("#table-new-race-" + singleRaceDetailID).bootstrapTable({
      data: raceresults,
      sortName: 'finalpos',
      columns: [{
          field: 'finalpos',
          title: '',
          visible: false
      }, {
          field: 'racerid',
          title: 'Name'
      }, {
          field: 'lapcount',
          title: 'Laps'
      }, {
          field: 'racetime',
          title: 'Time'
      }, {
          field: 'fastlap',
          title: 'FastLap'
      }]
    });
  })
};
