<template>
  <form class="certificateVerificationForm starterForm form">
    <fieldset>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isHostValid }"
      >
        <label for="host">Host <span class="required">Required</span></label>
        <input
          type="text"
          name="host"
          id="host"
          v-model="certHost"
          @blur="onHostBlur"
          placeholder="example.com"
          required
        />
        <p
          v-if="!isHostValid"
          class="inputWrapper__help inputWrapper__help--error"
        >
          Host doesn't seem to be a valid certificate host.
        </p>
      </div>
      <div class="inputWrapper">
        <label for="port">Port</label>
        <input type="text" name="port" id="port" v-model="certPort" required />
        <p class="inputWrapper__help">
          If left empty, host will default to 443.
        </p>
      </div>
      <div class="inputWrapper certificateVerificationForm__delay">
        <label for="delay">
          Expiration delay <span class="required">Required</span>
        </label>
        <div>
          <input
            type="number"
            name="delay"
            id="delay"
            min="1"
            :max="maxDelay"
            @blur="enforceDelayMinMax"
            v-model="certDelayNumber"
            required
          />
          <select
            name="delayUnit"
            id="delayUnit"
            v-model="certDelayUnit"
            @change="onDelayUnitChange"
            required
          >
            <option value="s">Seconds</option>
            <option value="m">Minutes</option>
            <option value="h">Hours</option>
            <option value="d">Days</option>
            <option value="w">Weeks</option>
          </select>
        </div>
      </div>
      <div class="inputWrapper">
        <label for="deploymentToken">Subject Alternative Names</label>
        <input
          type="text"
          name="altNames"
          id="altNames"
          v-model="certAltNames"
        />
        <p class="inputWrapper__help">
          Additional host names protected by the same vertificate,
          <strong>as a comma-separated list</strong>
        </p>
      </div>
      <div
        class="inputWrapper"
        :class="{ 'inputWrapper--error': !isFingerprintValid }"
      >
        <label for="deploymentToken">TLS Fingerprint</label>
        <input
          type="text"
          name="fingerprint"
          id="fingerprint"
          @blur="checkIfFinferprintIsValid"
          v-model="certFingerprint"
        />
        <p
          v-if="!isFingerprintValid"
          class="inputWrapper__help inputWrapper__help--error"
        >
          FingerPrint is not a valid SHA256
        </p>
        <p class="inputWrapper__help">
          The TLS Fingerprint as a SHA256. As the fingerprint changes at each
          certificate renewal, you will have to provide the new one each time
          your certificate is renewed. Leave empty if you want to automate and
          use the same verification even after renewals.
        </p>
      </div>
      <div class="inputWrapper">
        <label for="deploymentToken">Issuer</label>
        <input
          type="text"
          name="issuer"
          id="issuer"
          placeholder="CN=R3,O=Let's Encrypt,C=US"
          v-model="certIssuer"
        />
      </div>
      <details class="inputWrapper inputWrapper--details">
        <summary>Contributions and tags</summary>
        <ExperimentContributions v-model="contributions" />
        <ExperimentTags v-model="tags" />
      </details>
      <div class="inputWrapper">
        <button
          @click.prevent="create(false)"
          :disabled="isSubmitDisabled"
          class="button button--primary"
        >
          Create
        </button>
        <button
          @click.prevent="create(true)"
          :disabled="isSubmitDisabled"
          class="button button--creative"
        >
          Create and run
        </button>
      </div>
    </fieldset>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type {
  EnvConfiguration,
  ExperimentDefinition,
  ExperimentImportPayload,
  Contributions,
} from "@/types/experiments";
import { importExperiment } from "@/stores/experiments";
import ExperimentContributions from "@/components/experiments/ExperimentContributions.vue";
import ExperimentTags from "@/components/experiments/ExperimentTags.vue";

const certHost = ref<string>("");
const isHostValid = ref<boolean>(true);
const onHostBlur = (): void => {
  if (certHost.value === "") {
    isHostValid.value = true;
  } else {
    if (!certHost.value.includes(".")) {
      isHostValid.value = false;
    } else if (certHost.value.includes(" ")) {
      isHostValid.value = false;
    }
  }
};

const certPort = ref<string>("");
const computedCertPort = computed<string>(() => {
  return certPort.value === "" ? "443" : certPort.value;
});

const certDelayNumber = ref<number>(7);
const certDelayUnit = ref<string>("d");
const maxDelay = computed<number>(() => {
  if (certDelayUnit.value === "s" || certDelayUnit.value === "m") {
    return 60;
  } else if (certDelayUnit.value === "h") {
    return 24;
  } else if (certDelayUnit.value === "d") {
    return 31;
  } else if (certDelayUnit.value === "w") {
    return 4;
  } else {
    // Should never happen. Better safe than sorry.
    return 100;
  }
});
const onDelayUnitChange = (): void => {
  if (certDelayNumber.value > maxDelay.value) {
    certDelayNumber.value = maxDelay.value;
  }
};
const enforceDelayMinMax = (): void => {
  if (certDelayNumber.value < 0) {
    certDelayNumber.value = 0;
  }
  if (certDelayNumber.value > maxDelay.value) {
    certDelayNumber.value = maxDelay.value;
  }
};

const certAltNames = ref<string>("");
const computedCertAltNames = computed<string[]>(() => {
  let cleanStr: string = certAltNames.value.replace(/\s+/g, "");
  return cleanStr.split(",");
});

const certFingerprint = ref<string>("");
const isFingerprintValid = ref<boolean>(true);
const checkIfFinferprintIsValid = (): void => {
  if (certFingerprint.value === "") {
    isFingerprintValid.value = true;
  } else {
    const fingerPrintRegex = new RegExp("\b[A-Fa-f0-9]{64}\b");
    isFingerprintValid.value = fingerPrintRegex.test(certFingerprint.value);
  }
};

const certIssuer = ref<string>("");

const contributions = ref<Contributions>({
  availability: "high",
  latency: "none",
  security: "high",
  errors: "none",
});

const tags = ref<string[]>(["tls", "certificate", "security"]);

let verification: ExperimentDefinition = {
  version: "1.0.0",
  title: "Certificate is always valid and has not expired",
  configuration: {
    reliably_host: {
        type: "env",
        key: "RELIABLY_PARAM_HOST",
    },
    reliably_port: {
        type: "env",
        key: "RELIABLY_PARAM_PORT",
        default: 443,
    },
    reliably_issuer: {
        type: "env",
        key: "RELIABLY_PARAM_ISSUER",
    },
    reliably_expire_after: {
        type: "env",
        key: "RELIABLY_PARAM_EXPIRES_AFTER",
    },
    reliably_alt_names: {
        type: "env",
        key: "RELIABLY_PARAM_ALT_NAMES",
    },
    reliably_fingerprint: {
        type: "env",
        key: "RELIABLY_PARAM_FINGERPRINT",
    },
  },
  description:
    "Verify the certificate of a remote endpoint for particular aspects: expiration date, alternative subject names, issuer and fingerprint",
  "steady-state-hypothesis": {
    title: "Capture certificate and perform the checks",
    probes: [
      {
        type: "probe",
        name: "capture-certificate",
        tolerance: {
          type: "probe",
          name: "verifiy-tls-certificate",
          provider: {
            type: "python",
            module: "chaosreliably.activities.tls.tolerances",
            func: "verify_tls_cert",
            arguments: {
              expire_after: "${reliably_expire_after}",
              alt_names: "${reliably_alt_names}",
              fingerprint_sha256: "${reliably_fingerprint}",
              issuer: "${reliably_issuer}",
            },
          },
        },
        provider: {
          type: "python",
          module: "chaosreliably.activities.tls.probes",
          func: "get_certificate_info",
          arguments: {
            host: "${reliably_host}",
            port: "${reliably_port}",
          },
        },
      },
    ],
  },
  method: [],
  extensions: [
    {
        name: "chatgpt",
        messages: [
            {
                role: "user",
                content: "What are the impacts of an expired TLS certificate?",
            },
            {
                role: "user",
                content: "How can I monitor my certificates?",
            },
            {
                role: "user",
                content: "What are the properties of a TLS certificate that I should be reviewing periodically?",
            }
        ]
    }
  ]
};

const isSubmitDisabled = computed<boolean>(() => {
  return (
    certHost.value === "" || !isHostValid.value || !isFingerprintValid.value
  );
});

const create = async (run: boolean) => {
  if (!isSubmitDisabled.value) {
    verification.contributions = contributions.value;
    verification.tags = tags.value;
    (verification.configuration!.reliably_host as EnvConfiguration).default = certHost.value;
    (verification.configuration!.reliably_port as EnvConfiguration).default = computedCertPort.value;
    (verification.configuration!.reliably_expire_after as EnvConfiguration).default = certDelayNumber.value.toString() + certDelayUnit.value;
    (verification.configuration!.reliably_alt_names as EnvConfiguration).default = computedCertAltNames.value;
    (verification.configuration!.reliably_fingerprint as EnvConfiguration).default = certFingerprint.value;
    (verification.configuration!.reliably_issuer as EnvConfiguration).default = certIssuer.value;
    let e: ExperimentImportPayload = {
      experiment: JSON.stringify(verification),
    };
    if (run) {
      await importExperiment(e, true);
    } else {
      await importExperiment(e);
    }
  }
};
</script>

<style lang="scss" scoped>
.certificateVerificationForm {
  &__delay {
    > div {
      display: flex;
      flex-wrap: wrap;
      gap: var(--space-small);

      > input,
      > select {
        width: 12rem;
      }
    }
  }
}
</style>
