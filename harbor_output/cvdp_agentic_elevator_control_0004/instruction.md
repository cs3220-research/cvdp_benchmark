Modify the elevator control system to support overload detection and direction indicators (LEDs), while retaining its core functionality of managing multiple floors, handling call requests, and responding to emergency stops. The updated module now includes an `overload` input to simulate elevator weight overload, and additional outputs `up_led`, `down_led`, and `overload_led` to reflect current operational status.

---

### **Design Specification**

The `elevator_control_system` module is an FSM-based design that manages elevator movement across `N` floors, processes floor requests, handles emergency stops, and opens/closes doors automatically. The enhanced version now includes **overload protection** and **direction indication via LEDs**.

**New Functional Features**
1. **Overload Detection**
   - Input signal: `overload`
   - When `overload = 1`, the elevator halts in its current state and transitions to the `DOOR_OPEN` state if not already there.
   - Doors remain open during overload.
   - Elevator movement is disabled until the overload is cleared (`overload = 0`).
   - Output signal: `overload_led = 1` when overload is active.

2. **Direction LEDs**
   - `up_led = 1` when the elevator is moving up (`MOVING_UP` state).
   - `down_led = 1` when the elevator is moving down (`MOVING_DOWN` state).
   - Both LEDs are deactivated in `IDLE`, `DOOR_OPEN`, or `EMERGENCY_HALT` states.

---

### **Operational Behavior**

**State Transitions**
- **IDLE**: Waits for a request. If `overload` is active, it transitions directly to `DOOR_OPEN`.
- **MOVING_UP / MOVING_DOWN**: Moves floor-by-floor based on pending requests. Transitions to `DOOR_OPEN` when a requested floor is reached.
- **DOOR_OPEN**: Keeps doors open for a predefined duration. If `overload = 1`, the doors remain open indefinitely until the overload clears.
- **EMERGENCY_HALT**: Activated by `emergency_stop`. Resumes to IDLE once the signal is deactivated.

**Priority Logic**
- Requests are served based on current direction:
  - Upward requests take priority when going up.
  - Downward requests take priority when descending.
- If no request remains in the current direction, the system returns to IDLE.

---

### **Example Scenarios**

**Example 1: Overload During Movement**
- **Input**:
  - Current floor: 5, Requested floor: 2
  - `overload` = 1 triggered while elevator is moving down
- **Expected Behavior**:
  - Elevator halts immediately
  - Door opens and stays open
  - `overload_led` = 1
  - After clearing overload, elevator resumes to floor 2

**Example 2: Direction LED Behavior**
- **Input**:
  - Request floor 3 from ground floor
- **Expected Behavior**:
  - `up_led` = 1 while elevator ascends
  - `down_led` = 0
  - Once door opens, both LEDs turn off

**Example 3: Overload While Idle**
- **Input**:
  - No active requests, `overload = 1`
- **Expected Behavior**:
  - Elevator stays in `DOOR_OPEN` state
  - `overload_led` = 1
  - No movement until overload clears
