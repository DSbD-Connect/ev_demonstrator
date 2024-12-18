//status_api = "http://192.168.0.3:5556/api/status/"
//stop_api = "http://192.168.0.3:5556/api/stop/"


status_api = "https://dsbd-cms-001.loca.lt/api/status/"
stop_api = "https://dsbd-cms-001.loca.lt/api/stop/"
login_api = "https://dsbd-cms-001.loca.lt/api/login"
card_provider_api = "https://dsbd-cms-001.loca.lt/api/card_provider"

export function get_start_api(charging_api, username, vehicle_id){
    return charging_api + "&username=" + username + "&vehicle_id=" + btoa(vehicle_id) 
}

export function get_status_api(charging_point_id){
    return status_api + charging_point_id
}

export function get_stop_api(charging_point_id){
    return stop_api + charging_point_id
}

export function get_login_api(){
    return login_api
}

export function get_card_provider_api(){
    return card_provider_api
}
