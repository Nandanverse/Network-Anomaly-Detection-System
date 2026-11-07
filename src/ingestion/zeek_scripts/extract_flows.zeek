@load base/protocols/conn
@load base/protocols/http
@load base/protocols/dns
@load base/protocols/ssl
@load base/frameworks/notice

redef Connection::track_all = T;

global flow_log: Log::ID = Log::create_stream(flow, [$columns=FlowInfo, $path="flows"]);

type FlowInfo: record {
    ts: time &log;
    uid: string &log;
    id_orig_h: addr &log;
    id_orig_p: port &log;
    id_resp_h: addr &log;
    id_resp_p: port &log;
    proto: string &log;
    service: string &log &optional;
    duration: interval &log &optional;
    orig_bytes: count &log &optional;
    resp_bytes: count &log &optional;
    conn_state: string &log &optional;
    local_orig: bool &log &optional;
    local_resp: bool &log &optional;
    missed_bytes: count &log &optional;
    history: string &log &optional;
    orig_pkts: count &log &optional;
    orig_ip_bytes: count &log &optional;
    resp_pkts: count &log &optional;
    resp_ip_bytes: count &log &optional;
    tunnel_parents: set[string] &log &optional;
    label: string &log &optional;
    detailed_label: string &log &optional;
};

event connection_state_remove(c: connection) {
    local f: FlowInfo = [$ts=c$start_time, $uid=c$uid, $id_orig_h=c$id$orig_h, $id_orig_p=c$id$orig_p, $id_resp_h=c$id$resp_h, $id_resp_p=c$id$resp_p, $proto=c$proto, $service=c$service, $duration=c$duration, $orig_bytes=c$orig_bytes, $resp_bytes=c$resp_bytes, $conn_state=c$conn_state, $local_orig=c$local_orig, $local_resp=c$local_resp, $missed_bytes=c$missed_bytes, $history=c$history, $orig_pkts=c$orig_pkts, $orig_ip_bytes=c$orig_ip_bytes, $resp_pkts=c$resp_pkts, $resp_ip_bytes=c$resp_ip_bytes, $tunnel_parents=c$tunnel_parents];
    Log::write(flow_log, f);
}

event zeek_init() {
    Log::set_buf_size(flow_log, 1024);
    Log::set_buf_flush_interval(flow_log, 10sec);
}