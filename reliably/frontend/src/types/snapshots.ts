import type { Environment } from "@/types/environments";

export interface SnapshotDiscoveryMeta {
    name: string;
    display: string;
    dt: Date;
    kind: string;
    platform?: string;
    category: string;
}

export interface SnapshotDiscoveryGCPMeta extends SnapshotDiscoveryMeta {
    project?: string;
    region?: string;
    zone?: string;
    self_link?: string;
    regional?: boolean;
}

export interface SnapshotDiscoveryK8SMeta extends SnapshotDiscoveryMeta {
    ns: string;
}

export interface SnapshotDiscoveryAWSMeta extends SnapshotDiscoveryMeta {
    region: string;
}

export interface SnapshotDiscoveryLink {
    direction: string;
    kind: string;
    path: string;
    pointer: string;
    id: string;
}

export interface SnapshotDiscoveryLinkInfo {
    id: string,
    meta: SnapshotDiscoveryMeta | SnapshotDiscoveryGCPMeta | SnapshotDiscoveryK8SMeta | SnapshotDiscoveryAWSMeta;
}

export interface SnapshotDiscoveryResource {
    id: string;
    meta: SnapshotDiscoveryMeta | SnapshotDiscoveryGCPMeta | SnapshotDiscoveryK8SMeta | SnapshotDiscoveryAWSMeta;
    links: SnapshotDiscoveryLink[];
    struct: Object;
}

export interface SnapshotDiscovery {
    id: string;
    meta: SnapshotDiscoveryMeta;
    resources: SnapshotDiscoveryResource[];
}

export interface Snapshot {
    id?: string;
    org_id?: string;
    user_id?: string;
    created_date?: Date | string;
    snapshot: SnapshotDiscovery;
}

export interface SnapshotsApiJsonResponse {
    items: SnapshotDiscoveryResource[];
    count: number;
}

export interface ResourceLinksInfoApiJsonResponse {
    items: SnapshotDiscoveryLinkInfo[];
    count: number;
}

export interface SnapshotsPage {
    page: number;
    resources: SnapshotDiscoveryResource[];
    total: number;
    isReady: boolean;
}

export interface ResourceLinksInfoPage {
    page: number;
    links: SnapshotDiscoveryLinkInfo[];
    total: number;
    isReady: boolean;
}

export interface NewSnapshot {
    vendors: string[],
    integration_id: string,
}


export interface CandidatesApiJsonResponse {
    items: Candidate[];
    count: number;
}

export interface Candidate {
    val: string,
    label: string
}

export interface CandidatesPage {
    page: number;
    candidates: Candidate[];
    total: number;
    isReady: boolean;
}

export interface FieldsState {
    key: string,
    val: string,
}

export interface SnapshotConfiguration {
    name: string,
    integration_id: string,
    env: Environment
}
