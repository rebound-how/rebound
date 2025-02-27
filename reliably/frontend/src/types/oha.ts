export interface OhaSummary {
  total: number;
  average: number;
  fastest: number;
  slowest: number;
  totalData: number;
  sizePerSec: number;
  successRate: number;
  requestsPerSec: number;
  sizePerRequest: number;
}

export interface OhaResponseTimeHistogram {
  [key: string]: number;
}

export interface OhaLatencyPercentiles {
  p10: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
  p95: number;
  p99: number;
  "p99.9": number;
  "p99.99": number;
}

export interface OhaStatusCodeDistribution {
  [key: string]: number;
}

export interface OhaErrorDistribution {
  [key: string]: number;
}

export interface OhaDetailsDNS {
  average: number;
  fastest: number;
  slowest: number;
}

export interface OhaDetails {
  DNSDialup: OhaDetailsDNS;
  DNSLookup: OhaDetailsDNS;
}

export interface OhaRpsPercentiles {
  p10: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
  p95: number;
  p99: number;
  "p99.9": number;
  "p99.99": number;
}

export interface OhaRps {
  max: number;
  mean: number;
  stddev: number;
  percentiles: OhaRpsPercentiles;
}

export interface OhaOutput {
  summary: OhaSummary;
  details: OhaDetails;
  rps: OhaRps;
  statusCodeDistribution: OhaStatusCodeDistribution;
  responseTimeHistogram: OhaResponseTimeHistogram;
  responseTimeHistogramSuccessful: OhaResponseTimeHistogram;
  responseTimeHistogramNotSuccessful: OhaResponseTimeHistogram;
  latencyPercentiles: OhaLatencyPercentiles;
  latencyPercentilesSuccessful: OhaLatencyPercentiles;
  latencyPercentilesNotSuccessful: OhaLatencyPercentiles;
  errorDistribution: OhaErrorDistribution;
}
