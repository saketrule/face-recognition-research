
$(document).ready(function(){
    // connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var session = null, trainTab=false, train=null;

    //////////////////////////
    //    Layout setup
    //////////////////////////

	function populateMenu(tab){
		if (tab=='run'){
			$('#trainTabButton')[0].innerHTML='Train Tab';
			$('#menuId')[0].innerHTML=' \
			<div id="runMenu"> \
			<div style="float:right"> \
			  <button type="button" id="startSessionButton"> Start Session </button> \
			  <button type="button" id="stopSessionButton" disabled> Stop Session </button> \
			  <button type="button" id="saveSessionButton" disabled> Save Session </button> \
			</div> \
			<div> \
			  <button type="button" id="snapAndRecognizeButton"> Snap & Recognize </button> \
			  <div style="float:left; margin-left:10px"> \
				<button type="button" id="startCameraScanButton"> Start camera scan </button> \
				<button type="button" id="stopCameraScanButton" disabled> Stop camera scan </button> \
			  </div> \
			  <div style="float:left; margin-left:10px"> \
				<button type="button" id="startFolderScanButton"> Start saved session scan </button> \
				<button type="button" id="stopFolderScanButton" disabled> Stop saved session scan </button> \
			  </div> \
				</div>';
		}
		else if(tab=='train'){
			$('#trainTabButton')[0].innerHTML='Run Tab';
			$('#menuId')[0].innerHTML = ' \
				<button type="button" id="snapTrainImageButton"> Take Image </button> \
				<input type="text" id="peopleInput" placeholder="Number of people" /> \
                <button type="button" id="clusterButton"> Cluster </button> \
				<button type="button" id="addPeople"> Add People </button> \
				<button type="button" id="trainClassifierButton" style="width:150px"> Train Classifier </button> ';
            
            train = {'id':null,'labels':null,'images':null} // Saket Note: Correctly initialize, may not need all this
		}
	}
	////  Default run tab opened
	populateMenu('run');


	//////////////////////////
	//    Button listeners
	//////////////////////////

	// To toggle train/run tabs
	$(document).on('click','#trainTabButton',function(){
		console.log('[#trainTabButton] clicked');
		if (trainTab == false){
			trainTab = true;
			populateMenu('train');
			socket.emit('trainReq',{'type':'trainOn'});
		}
		else{
			trainTab = false;
			populateMenu('run');
			socket.emit('trainReq',{'type':'trainOff'});
		}
	});

		//////////////////////////
		// Training buttons
		//////////////////////////

	$(document).on('click','#snapTrainImageButton',function(){
		console.log('[#snapTrainImageButton] clicked');
		data = {'type':'takeImage'};
		socket.emit('trainReq',data);
	});

	$(document).on('click','#clusterButton',function(){
		console.log('[#clusterButton] clicked');
        var peopleNumber = $('#peopleInput')[0].value;
        if(peopleNumber==""){
            alert("Please enter number of people");
            return;
        } else {
			try {
				var people = parseInt(peopleNumber);
			} catch(exp){
				alert("Enter a valid number of people");
				return;
			}
	}
		data = {'type': 'cluster','people':parseInt(peopleNumber)};
		socket.emit('trainReq',data);
	});

	$(document).on('click','#addPeople',function(){
		console.log('[#addPeople] clicked');
        peopleData = collectClusterData();
        console.log(peopleData);
        $('#info-div')[0].innerHTML="People added! :)";
		data = {'type': 'addPeople', 'peopleData':peopleData};
		socket.emit('trainReq',data);
	});

	$(document).on('click','#trainClassifierButton',function(){
		console.log('[#trainClassifierButton] clicked');
		data = {'type': 'trainClassifier'};
		socket.emit('trainReq',data);
	});

		//////////////////////////
		// Run buttons
		//////////////////////////

	$(document).on('click','#snapAndRecognizeButton',function(){
    	console.log('[#snapAndRecognizeButton] Clicked');
    	data = {'type':'snapAndRecognize'};
    	socket.emit('req',data);
    });

    $(document).on('click','#startSessionButton',function(){
    	console.log('[#startSessionButton] clicked');
    	session = {'id':null, 'list':{}, 'images':null}
    	data = {'type':'startSession'};
    	socket.emit('req',data);
    	$('#startSessionButton').attr('disabled','disabled');
    	$('#stopSessionButton').removeAttr('disabled');
    });

    $(document).on('click','#stopSessionButton',function(){
    	console.log('[#stopSessionButton] clicked');
    	data = {'type':'stopSession'};
    	socket.emit('req',data);
    	$('#stopSessionButton').attr('disabled','disabled');
    	$('#startSessionButton').removeAttr('disabled');
      $('#saveSessionButton').removeAttr('disabled');
    });

    $(document).on('click','#startCameraScanButton',function(){
    	console.log('[#startCameraScan] clicked');
    	data = {'type':'startCameraScan'};
    	socket.emit('req',data);
    	$('#startCameraScanButton').attr('disabled','disabled');
      $('#saveCameraScanButton').attr('disabled','disabled');
    	$('#stopCameraScanButton').removeAttr('disabled');
    });

    $(document).on('click','#stopCameraScanButton',function(){
    	console.log('[#stopCameraScan] clicked');
    	data = {'type':'stopCameraScan'};
    	socket.emit('req',data);
    	$('#stopCameraScanButton').attr('disabled','disabled');
    	$('#startCameraScanButton').removeAttr('disabled');
    });

    $(document).on('click','#startFolderScanButton',function(){
    	console.log('[#startFolderScan] clicked');
    	data = {'type':'startFolderScan','sessionId':'Session8'};
    	socket.emit('req',data);
    	$('#startFolderScanButton').attr('disabled','disabled');
    	$('#stopFolderScanButton').removeAttr('disabled');
    });

    $(document).on('click','#stopFolderScanButton',function(){
    	console.log('[#stopFolderScan] clicked');
    	data = {'type':'stopFolderScan'};
    	socket.emit('req',data);
    	$('#stopFolderScanButton').attr('disabled','disabled');
    	$('#startFolderScanButton').removeAttr('disabled');
    });

    //////////////////////////
    //     Server listeners
    //////////////////////////
    socket.on('update', function(data){
    	if('image' in data){
			console.log('[server - update image]');
    		$('#myimage').attr("src",data['image']);
            if ('image_id' in data){
                $('#info-div')[0].innerHTML = data['image_id'];
            }
    	};
    	if(session!=null){
    		if('session' in data){
				console.log('[server - update session]');
    			var newSession = data['session'];
          var newList = newSession['list'];
          var itms=[],newitms=[];
          for(var id in newList){
            if(id in session['list']){
              itms.push([newList[id]['id'],newList[id]['name'],newList[id]['conf']]);
            }
            else{
              newitms.push([newList[id]['id'],newList[id]['name'],newList[id]['conf']]);
            }
          }
          $('#list-body').html(make_list_item(itms,newitms));
          session = newSession;
    		}
    	};
    });


    socket.on('trainUpdate', function(data){
        console.log('[server - trainUpdate] '+ data['type']);
        reqType = data['type'];
        if (reqType == 'showClusters'){
            // make sure cluster id is passed "tag" ; call assert when backend is done 
            showClusters(data['clusters']);
            // Clusters should be in format {id:[images]}
            // Show clusters, make UI for labelling
        }
    }); 



    //////////////////////////
    //     Helper functions
    //////////////////////////

    function make_list_item(itms,newitms){
        var mylist = "";
        // New people updated at the top list
        for(var ind=0;ind<newitms.length;ind++){
            var new_tr = '<tr class="newname">\n';
            if(newitms[ind][2]>=1){
                new_tr = '<tr class="newname" style="background-color:beige;">\n';
                newitms[ind][2] = 1;
            }
            for (var i=0;i<newitms[ind].length; i++){
                new_tr += "<td> " + newitms[ind][i] + "</td>\n";
            }
            new_tr += "</tr>\n";
            mylist += new_tr + "\n";
        }
        for(var ind=0;ind<itms.length;ind++){
            var new_tr = "<tr>\n";
            if(itms[ind][2]>=1){
                new_tr = '<tr class="newname" style="background-color:beige;">\n';
                itms[ind][2] = 1;
            }
            for (var i=0;i<itms[ind].length; i++){
                new_tr += "<td> " + itms[ind][i] + "</td>\n";
            }
            new_tr += "</tr>\n";
            mylist += new_tr + "\n";
        }
        return mylist
    };

    function collectClusterData(){
        var data = [];
        var rows = $('#clusterTableBodyId').children();
        for (var i=0; i<rows.length; i++){
            data.push([rows[i].getElementsByClassName('nameInput')[0].value,rows[i].getElementsByClassName('idInput')[0].value]);
        }
        return data;
    }
    function showClusters(clusters){
        var body = document.getElementById('info-div');
        var tbl = document.createElement('table');
        tbl.style.width = '100%';
        tbl.setAttribute('border', '1');
        var tbdy = document.createElement('tbody');
        tbdy.setAttribute('id','clusterTableBodyId');
        for (var cId in clusters) {
            var tr = document.createElement('tr');
            for (var j = 0; j < 3; j++) {
                var td = document.createElement('td');
                var img = document.createElement('img');
                img.setAttribute('src',clusters[cId][j]);
                img.setAttribute('height','70px');
                td.appendChild(img);
                tr.appendChild(td);
            }
            var td = document.createElement('td');
            var nameInput = document.createElement('input');
            nameInput.setAttribute('placeholder','Name');
            nameInput.setAttribute('class','nameInput');
            var idInput = document.createElement('input');
            idInput.setAttribute('placeholder','Unique Id');
            idInput.setAttribute('class','idInput');
            td.appendChild(nameInput);
            td.appendChild(idInput);
            tr.appendChild(td);
            td.style.textAlign = 'center';
            tbdy.appendChild(tr);
        }
        tbl.appendChild(tbdy);
        body.innerHTML = "Name em";
        body.appendChild(tbl);
    }

});
