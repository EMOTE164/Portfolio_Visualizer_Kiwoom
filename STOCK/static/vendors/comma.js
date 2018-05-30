(function( $ ){
	function thousandSeparatorCommas ( number ){

	var string = "" + number;  // 문자로 바꾸기.

	string = string.replace( /[^-+\.\d]/g, "" )  // ±기호와 소수점, 숫자들만 남기고 전부 지우기.

	var regExp = /^([-+]?\d+)(\d{3})(\.\d+)?/;  // 필요한 정규식.

	while ( regExp.test( string ) ) string = string.replace( regExp, "$1" + "," + "$2" + "$3" );  // 쉼표 삽입.

	return string;
	}
	function changeText (){

	var demo1 = document.getElementById( "demo1" );

	var text = demo1.innerHTML;

	var change = thousandSeparatorCommas( text );

	demo1.innerHTML = change;
	}
	function changeAll (){

		 var demo2 = document.getElementById( "demo2" );

		 var text = demo2.innerHTML;

		 var reg = /[-+]?\d+/gm;    // 여러줄의 문장 전체에서 숫자를 찾는 정규식.

		 var change = text.replace( reg , function( str ){    return thousandSeparatorCommas( str );    } );

		 demo2.innerHTML = change;
	}

	var input = document.getElementById( "initial_money" );

	input.onkeyup = function( event ){

	// "shift 키 + 방향키"를 눌렀을 때에는 제외시키기.
	event = event || window.event;
	var keyCode = event.which || event.keyCode;
	if ( keyCode == 16 || ( 36 < keyCode && keyCode < 41 )) return;


	var cursor = getPositionOfCursor( this ); // 커서의 위치 가져오기.


	var beforeLength = this.value.length; // 원래 텍스트의 전체 길이

	this.value = thousandSeparatorCommas( this.value ); // 콤마 추가해서, 텍스트 바꿔주기

	var afterLength = this.value.length; // 바뀐 텍스트의 전체 길이

	var gap = afterLength - beforeLength;


	// 커서의 위치 바꾸기.
	if ( this.selectionStart ){
	 this.selectionStart = cursor.start + gap;
	 this.selectionEnd = cursor.end + gap;
	}

	else if ( this.createTextRange ){

	 var start = cursor.start - beforeLength;
	 var end = cursor.end - beforeLength;

	 var range = this.createTextRange();

	 range.collapse( false );
	 range.moveStart ( "character",  start );
	 range.moveEnd ( "character", end );
	 range.select();
	}
	};


	function getPositionOfCursor ( tag ){

	var position = { start: 0 , end: 0 };


	// ie 10 이상 & 그외 브라우저.
	if ( tag.selectionStart ){
	 position.start = tag.selectionStart;
	 position.end = tag.selectionEnd;
	}


	// ie 9 이하.
	else if ( document.selection ){
	 var range = document.selection.createRange();

	 var copyRange = range.duplicate();
				copyRange.expand( "textedit" );
				copyRange.setEndPoint( "EndToEnd" , range );

	 var start = copyRange.text.length - range.text.length;
	 var end = start - range.text.length;

	 position.start = parseInt( start );
	 position.end = parseInt( end );
	}

	return  position;
	}


})(  );
