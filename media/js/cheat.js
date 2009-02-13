function selectState(turn,stateId,stateName,color) {
  $("selectedStateName").innerHTML = stateName;
  $('id_turn').value = turn;
  $('id_state').value = stateId;
  setStyle($("selectedStateName").parentNode,{ 'background-color' : color	});
  $('submitbutton').disabled = false;
}
