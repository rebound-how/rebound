<template>
  <div class="activitySelector">
    <form class="activitiesFilters form">
      <div class="inputWrapper">
        <label for="afTarget">Target</label>
        <select id="afTarget" name="afTarget" v-model="filterTarget">
          <option value="all">All</option>
          <option value="chaosaws">AWS</option>
          <option value="azchaosaws">AWS AZ</option>
          <option value="chaosazure">Azure</option>
          <option value="chaosdynatrace">Dynatrace</option>
          <option value="chaosgandi">Gandi</option>
          <option value="chaosgcp">Google Cloud</option>
          <option value="chaosk6">Grafana k6</option>
          <option value="chaoshoneycomb">Honeycomb</option>
          <option value="chaosistio">Istio</option>
          <option value="chaosk8s">Kubernetes</option>
          <option value="chaosfault">fault</option>
          <option value="chaosprometheus">Prometheus</option>
          <option value="chaosreliably">Reliably</option>
          <option value="chaosservicefabric">Service Fabric</option>
          <option value="chaosspring">Spring</option>
          <option value="chaostoxi">ToxiProxy</option>
          <option value="chaoswm">WireMock</option>
        </select>
      </div>
      <div class="inputWrapper">
        <label for="afCategory">Service</label>
        <select id="afCategory" name="afCategory" v-model="filterCategory">
          <option value="">Select a target provider first</option>
        </select>
      </div>
      <div class="inputWrapper">
        <label for="afType">Type</label>
        <select id="afType" name="afType" v-model="filterType">
          <option value="all">All</option>
          <option value="actions">Actions</option>
          <option value="probes">Probes</option>
          <option value="tolerances">Tolerances</option>
          <option value="utils">Utils</option>
        </select>
      </div>
    </form>
    <ul class="activitySelector__list list-reset" id="activitiesList">
      <template v-for="(a, index) in actvts">
        <li v-if="isActivityValid(a)" :key="index">
          <ActivityButton :activity="a" @select-activity="selectActivity" />
        </li>
      </template>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { toRefs, ref, watch, onMounted } from "vue";
import { activities, fetchActivities } from "@/stores/activities";
import { useStore } from "@nanostores/vue";

import type { Activity } from "@/types/ui-types";

import ActivityButton from "@/components/starters/ActivityButton.vue";

const props = defineProps<{
  to: string;
  where?: string;
  index?: number;
}>();
const { to, where, index } = toRefs(props);

const actvts = useStore(activities);

const emit = defineEmits<{
  (e: "addActivity", id: string, to: string): void;
  (e: "close"): void;
}>();

function selectActivity(id: string) {
  emit("addActivity", id, to.value);
  emit("close");
}

function isActivityValid(a: Activity): boolean {
  if (to.value === "hypothesis") {
    return a.type === "probe";
  } else if (to.value === "rollbacks") {
    return a.type === "action";
  } else {
    return true;
  }
}

const GANDICATEGORIES = [
  {
    name: "domains",
    displayName: "Domains",
  },
];

const AWSCATEGORIES = [
  {
    name: "asg",
    displayName: "ASG",
  },
  {
    name: "cloudwatch",
    displayName: "CloudWatch",
  },
  {
    name: "ec2",
    displayName: "EC2",
  },
  {
    name: "ecs",
    displayName: "ECS",
  },
  {
    name: "eks",
    displayName: "EKS",
  },
  {
    name: "elasticache",
    displayName: "ElastiCache",
  },
  {
    name: "elbv2",
    displayName: "ELBv2",
  },
  {
    name: "emr",
    displayName: "EMR",
  },
  {
    name: "fis",
    displayName: "FIS",
  },
  {
    name: "iam",
    displayName: "IAM",
  },
  {
    name: "incidents",
    displayName: "Incidents",
  },
  {
    name: "awslambda",
    displayName: "Lambda",
  },
  {
    name: "rds",
    displayName: "RDS",
  },
  {
    name: "route53",
    displayName: "Route 53",
  },
  {
    name: "s3",
    displayName: "S3",
  },
  {
    name: "ssm",
    displayName: "SSM",
  },
  {
    name: "xray",
    displayName: "XRay",
  },
];

const AWSAZCATEGORIES = [
  {
    name: "asg",
    displayName: "ASG",
  },
  {
    name: "ec2",
    displayName: "EC2",
  },
  {
    name: "eks",
    displayName: "EKS",
  },
  {
    name: "elasticache",
    displayName: "ElastiCache",
  },
  {
    name: "elb",
    displayName: "ELB",
  },
  {
    name: "elbv2",
    displayName: "ELBv2",
  },
  {
    name: "mq",
    displayName: "Amazon MQ",
  },
];

const AZURECATEGORIES = [
  {
    name: "aks",
    displayName: "AKS",
  },
  {
    name: "machine",
    displayName: "Machine",
  },
  {
    name: "vmss",
    displayName: "VMSS",
  },
  {
    name: "webapp",
    displayName: "WebApp",
  },
];

const GCPCATEGORIES = [
  {
    name: "artifact",
    displayName: "Artifact",
  },
  {
    name: "cloudrun",
    displayName: "Cloud Run",
  },
  {
    name: "gke",
    displayName: "GKE",
  },
  {
    name: "lb",
    displayName: "Load Balancer",
  },
  {
    name: "monitoring",
    displayName: "Monitoring",
  },
  {
    name: "sql",
    displayName: "SQL",
  },
  {
    name: "storage",
    displayName: "Storage",
  },
];

const K8SCATEGORIES = [
  {
    name: "crd",
    displayName: "CRD",
  },
  {
    name: "deployment",
    displayName: "Deployment",
  },
  {
    name: "event",
    displayName: "Event",
  },
  {
    name: "networking",
    displayName: "Networking",
  },
  {
    name: "chaosmesh",
    displayName: "Stress",
  },
  {
    name: "node",
    displayName: "Node",
  },
  {
    name: "pod",
    displayName: "Pod",
  },
  {
    name: "service",
    displayName: "Service",
  },
  {
    name: "statefulset",
    displayName: "Statefulset",
  },
];

const TOXIPROXYCATEGORIES = [
  {
    name: "proxy",
    displayName: "Proxy",
  },
  {
    name: "toxic",
    displayName: "Toxic",
  },
];

const HONEYCOMBCATEGORIES = [
  {
    name: "SLO",
    displayName: "SLO",
  },
  {
    name: "marker",
    displayName: "Marker",
  },
  {
    name: "query",
    displayName: "Query",
  },
  {
    name: "trigger",
    displayName: "Trigger",
  },
];

const filterTarget = ref<string>("all");
const filterCategory = ref<string>("");
const filterType = ref<string>("");

watch(filterTarget, (newTarget) => {
  handleTargetChange(newTarget);
});

watch(filterCategory, (newCategory) => {
  handleCategoryChange(newCategory);
});

watch(filterType, (newType) => {
  handleTypeChange(newType);
});

function handleTargetChange(newTarget: string) {
  let catSelect = document.getElementById("afCategory");
  const s = catSelect as HTMLSelectElement;
  // First clear all options
  if (s !== null) {
    const s = catSelect as HTMLSelectElement;
    for (let i = s.options.length; i >= 0; i--) {
      s.remove(i);
    }
  }

  handleCategoryChange("all");

  let cats = [];
  if (newTarget === "all") {
    cats.push({ name: "", displayName: "Select a target provider first" });
  } else {
    cats = [{ name: "all", displayName: "All" }];

    if (newTarget === "chaosaws") {
      cats.push(...AWSCATEGORIES);
    } else if (newTarget === "azchaosaws") {
      cats.push(...AWSAZCATEGORIES);
    } else if (newTarget === "chaosazure") {
      cats.push(...AZURECATEGORIES);
    } else if (newTarget === "chaosgcp") {
      cats.push(...GCPCATEGORIES);
    } else if (newTarget === "chaosk8s") {
      cats.push(...K8SCATEGORIES);
    } else if (newTarget === "chaostoxi") {
      cats.push(...TOXIPROXYCATEGORIES);
    } else if (newTarget === "chaoshoneycomb") {
      cats.push(...HONEYCOMBCATEGORIES);
    }
  }

  cats.forEach((cat) => {
    let opt = new Option(cat.displayName, cat.name);
    s.add(opt);
  });

  let activities = document.querySelectorAll("#activitiesList > li");
  activities.forEach((act) => {
    if (newTarget === "all") {
      act.classList.remove("hidden");
    } else {
      let button = act.querySelector(".activityButton");
      if (button !== null) {
        if ((button as HTMLButtonElement).dataset.target !== newTarget) {
          act.classList.add("hidden");
        } else {
          act.classList.remove("hidden");
        }
      }
    }
  });
}

function handleCategoryChange(newCategory: string) {
  filterCategory.value = newCategory;
  let activities = document.querySelectorAll("#activitiesList > li");
  activities.forEach((act) => {
    if (newCategory === "all") {
      act.classList.remove("hiddenCategory");
    } else {
      let button = act.querySelector(".activityButton");
      if (button !== null) {
        if ((button as HTMLButtonElement).dataset.category !== newCategory) {
          act.classList.add("hiddenCategory");
        } else {
          act.classList.remove("hiddenCategory");
        }
      }
    }
  });

  handleTypeChange("all");
}

function handleTypeChange(newType: string) {
  filterType.value = newType;
  let activities = document.querySelectorAll("#activitiesList > li");
  activities.forEach((act) => {
    if (newType === "all") {
      act.classList.remove("hiddenType");
    } else {
      let button = act.querySelector(".activityButton");
      if (button !== null) {
        if ((button as HTMLButtonElement).dataset.type !== newType) {
          act.classList.add("hiddenType");
        } else {
          act.classList.remove("hiddenType");
        }
      }
    }
  });
}

onMounted(async () => {
  await fetchActivities();
});
</script>

<style lang="scss" scoped>
.activitySelector {
  padding: var(--space-small);

  .activitiesFilters {
    display: flex;
    flex-direction: column;
    gap: var(--space-medium);
    margin-bottom: var(--space-medium);
    padding: var(--space-small);

    background-color: var(--grey-100);
    border-radius: var(--border-radius-m);

    @media (min-width: 38rem) {
      flex-direction: row;
    }

    .inputWrapper {
      min-width: 12rem;
      margin-top: 0 !important;
    }
  }

  &__list {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-small);
    width: var(--max-width);
    max-width: 90vw;

    @media (min-width: 38rem) {
      grid-template-columns: repeat(2, 1fr);
    }

    @media (min-width: 54rem) {
      grid-template-columns: repeat(3, 1fr);
    }

    li {
      align-self: stretch;

      &.hidden,
      &.hiddenCategory,
      &.hiddenType {
        display: none;
      }
    }
  }
}
</style>
