	#Include <MsgBoxConstants.au3>
	#Include <IE.au3>
	#Include <Math.au3>

	; Set an escape hotkey to exit the script
	HotKeySet("{Esc}", "captureEsc")
	Func captureEsc()
		Exit
	EndFunc

	; Function to move the mouse with an accelerating-decelerating curve
	Func MoveMouseWithCurve($x, $y)
		Local $startX = MouseGetPos(0)
		Local $startY = MouseGetPos(1)
		Local $distance = Sqrt(($x - $startX)^2 + ($y - $startY)^2)
		Local $steps = Ceiling($distance / 10) ; Adaptive step count based on distance
		Local $speedFactor = 2 ; Base speed factor
		
		For $i = 1 To $steps
			Local $progress = $i / $steps
			Local $speedMultiplier = Exp(-4 * $progress) + 0.5 ; Start fast, slow down
			
			Local $intermediateX = $startX + ($x - $startX) * $progress
			Local $intermediateY = $startY + ($y - $startY) * $progress + (Sin($progress * 3.1416) * 5) ; Slight arc
			
			; Occasional overshoot near the target and correction
			If $i = Int($steps * 0.9) Then
				$intermediateX += Random(-3, 3, 1)
				$intermediateY += Random(-3, 3, 1)
			ElseIf $i = Int($steps * 0.95) Then
				$intermediateX -= Random(-2, 2, 1)
				$intermediateY -= Random(-2, 2, 1)
			EndIf
			
			MouseMove($intermediateX, $intermediateY, $speedFactor * $speedMultiplier)
		Next
	EndFunc

	; Function to read text from a specific screen coordinate
	Func ReadText($x, $y)
		MoveMouseWithCurve($x, $y)
		MouseClick($MOUSE_CLICK_LEFT) ; Single click to focus
		Sleep(50)
		MouseClick($MOUSE_CLICK_LEFT, $x, $y, 2) ; Double-click to select text
		Sleep(50)
		Send("^c") ; Copy selected text to clipboard
		Sleep(50)
		Return ClipGet()
	EndFunc

	; Function to check if float value is below the threshold
	Func CheckFloatValue($floatX, $floatY, $floatThreshold)
		Local $floatText = ReadText($floatX, $floatY)
		Local $floatValue = Number(StringRegExpReplace($floatText, "[^\d.]", ""))
		Return ($floatValue < $floatThreshold)
	EndFunc

	; Function to check if price is below the threshold
	Func CheckPrice($priceX, $priceY, $priceThreshold)
		Local $priceText = ReadText($priceX, $priceY)
		Local $price = Number(StringRegExpReplace($priceText, "[^\d.]", ""))
		Return ($price < $priceThreshold)
	EndFunc

	; Define an array with multiple item details (URL, title, float threshold, price threshold)
	; --- AutoIt Array Generated (6 items) ---
Global $arr_items[12][4] = [ _
    ["https://steamcommunity.com/market/listings/730/Dual%20Berettas%20%7C%20Stained%20%28Field-Tested%29", "Steam Community Market :: Listings for Dual Berettas | Stained (Field-Tested) - Google Chrome", "0.26", "8.5"], _
    ["https://steamcommunity.com/market/listings/730/M4A1-S%20%7C%20Boreal%20Forest%20%28Field-Tested%29", "Steam Community Market :: Listings for M4A1-S | Boreal Forest (Field-Tested) - Google Chrome", "0.26", "8.5"], _
    ["https://steamcommunity.com/market/listings/730/Nova%20%7C%20Candy%20Apple%20%28Field-Tested%29", "Steam Community Market :: Listings for Nova | Candy Apple (Field-Tested) - Google Chrome", "0.26", "8.5"], _
    ["https://steamcommunity.com/market/listings/730/P2000%20%7C%20Granite%20Marbleized%20%28Field-Tested%29", "Steam Community Market :: Listings for P2000 | Granite Marbleized (Field-Tested) - Google Chrome", "0.26", "8.5"], _
    ["https://steamcommunity.com/market/listings/730/UMP-45%20%7C%20Gunsmoke%20%28Field-Tested%29", "Steam Community Market :: Listings for UMP-45 | Gunsmoke (Field-Tested) - Google Chrome", "0.26", "8.5"], _
    ["https://steamcommunity.com/market/listings/730/XM1014%20%7C%20CaliCamo%20%28Field-Tested%29", "Steam Community Market :: Listings for XM1014 | CaliCamo (Field-Tested) - Google Chrome", "0.26", "8.5"], _
	["https://steamcommunity.com/market/listings/730/AUG%20%7C%20Condemned%20%28Field-Tested%29", "Steam Community Market :: Listings for AUG | Condemned (Field-Tested) - Google Chrome", "0.22", "10"], _
	["https://steamcommunity.com/market/listings/730/G3SG1%20%7C%20VariCamo%20%28Field-Tested%29", "Steam Community Market :: Listings for G3SG1 | VariCamo (Field-Tested) - Google Chrome", "0.22", "10"], _
	["https://steamcommunity.com/market/listings/730/Galil%20AR%20%7C%20VariCamo%20%28Field-Tested%29", "Steam Community Market :: Listings for Galil AR | VariCamo (Field-Tested) - Google Chrome", "0.22","10"], _
	["https://steamcommunity.com/market/listings/730/M249%20%7C%20Gator%20Mesh%20%28Field-Tested%29", "Steam Community Market :: Listings for M249 | Gator Mesh (Field-Tested) - Google Chrome", "0.22", "10"], _
	["https://steamcommunity.com/market/listings/730/MP9%20%7C%20Orange%20Peel%20%28Field-Tested%29", "Steam Community Market :: Listings for MP9 | Orange Peel (Field-Tested) - Google Chrome", "0.22", "10"], _
	["https://steamcommunity.com/market/listings/730/USP-S%20%7C%20Forest%20Leaves%20%28Field-Tested%29", "Steam Community Market :: Listings for USP-S | Forest Leaves (Field-Tested) - Google Chrome", "0.22", "10"] _
	]
	While True
		Sleep(2000)
		For $i = 0 To UBound($arr_items) - 1
			ShellExecute("chrome.exe", $arr_items[$i][0], "", "", @SW_MAXIMIZE)
			
			Local $waitTime = TimerInit()
			While Not WinActive($arr_items[$i][1])
				Sleep(500)
				If TimerDiff($waitTime) > 20000 Then
					WinClose($arr_items[$i][1])
					ContinueLoop
				EndIf
			WEnd

			Local $loadWaitTime = TimerInit()
			While (Hex(PixelGetColor(100, 244)) <> "001B2838")
				Sleep(1000)
				If TimerDiff($loadWaitTime) > 20000 Then
					WinClose($arr_items[$i][1])
					ContinueLoop
				EndIf
			WEnd

			Sleep(500)
			
			MoveMouseWithCurve(458, 200)
			Sleep(300)
			MouseClick($MOUSE_CLICK_LEFT)
			ToolTip("Hovering over 'Sort by Float' button", 356, 244)
			Sleep(250)
			
			Local $floatX = 539, $floatY = 329, $floatThreshold = Number($arr_items[$i][2])
			Local $priceX = 997, $priceY = 322, $priceThreshold = Number($arr_items[$i][3])
			Local $buyButtonX = 1070, $buyButtonY = 319

			If CheckFloatValue($floatX, $floatY, $floatThreshold) And CheckPrice($priceX, $priceY, $priceThreshold) Then
				MoveMouseWithCurve($buyButtonX, $buyButtonY)
				ToolTip("Hovering over Buy Button", $buyButtonX, $buyButtonY)
				Sleep(100)
				MouseClick($MOUSE_CLICK_LEFT)
				MoveMouseWithCurve(490,760)
				MouseClick($MOUSE_CLICK_LEFT)
				MoveMouseWithCurve(978,759)
				MouseClick($MOUSE_CLICK_LEFT)
				Sleep(1000)
				
			EndIf

			Sleep(50)
			WinClose($arr_items[$i][1])
			Sleep(50)
		Next
	WEnd
