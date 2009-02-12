function selectState(turn,stateId,stateName,color) {
  $("selectedStateName").innerHTML = stateName;
  $('id_turn').value = turn;
  $('id_state').value = stateId;
  setStyle($("selectedStateName"),{ 'background-color' : color	});
}
