---
template: landing.html
hide:
  - navigation
  - toc
  - path
---

#
<div class="tellme">
  <div class="why">
    <div class="tagline">
      <h2>A Rust-powered CLI that simulates network disruptions.</h2>
    </div>
    <div class="trailer">
      <script src="https://asciinema.org/a/l2pc0o8bBTJULesRrevcMuugc.js" id="asciicast-l2pc0o8bBTJULesRrevcMuugc" async="true"></script>
    </div>

    <div class="values">
      <div>
        <h2><span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path
                d="m13.13 22.19-1.63-3.83c1.57-.58 3.04-1.36 4.4-2.27zM5.64 12.5l-3.83-1.63 6.1-2.77C7 9.46 6.22 10.93 5.64 12.5M21.61 2.39S16.66.269 11 5.93c-2.19 2.19-3.5 4.6-4.35 6.71-.28.75-.09 1.57.46 2.13l2.13 2.12c.55.56 1.37.74 2.12.46A19.1 19.1 0 0 0 18.07 13c5.66-5.66 3.54-10.61 3.54-10.61m-7.07 7.07c-.78-.78-.78-2.05 0-2.83s2.05-.78 2.83 0c.77.78.78 2.05 0 2.83s-2.05.78-2.83 0m-5.66 7.07-1.41-1.41zM6.24 22l3.64-3.64c-.34-.09-.67-.24-.97-.45L4.83 22zM2 22h1.41l4.77-4.76-1.42-1.41L2 20.59zm0-2.83 4.09-4.08c-.21-.3-.36-.62-.45-.97L2 17.76z" />
            </svg>&nbsp;</span>Build A Core Strength</h2>
        <p>Practicing reliability brings the best of your skills and creativity.</p>
      </div>
      <div>
        <h2><span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path d="M12 1 3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5z" />
            </svg>&nbsp;</span>Protect Your Team</h2>
        <p>Explore, automate, reflect and prioritize reliability improvements to reduce incident anxiety.</p>
      </div>
      <div>
        <h2><span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path
                d="M14 19h8v-2h-8zm0-5.5h8v-2h-8zM14 8h8V6h-8zM2 12.5C2 8.92 4.92 6 8.5 6H9V4l3 3-3 3V8h-.5C6 8 4 10 4 12.5S6 17 8.5 17H12v2H8.5C4.92 19 2 16.08 2 12.5" />
            </svg>&nbsp;</span>Lock In Your Reliability Budget</h2>
        <p>Turn reliability from a "nice-to-have" into a can't-ignore line item.</p>
      </div>
    </div>
  <div class="animation-container">

    <!-- Phase 1 -->
    <svg class="phase-svg phase-1" viewBox="0 0 490 90">
      <circle class="node" cx="55" cy="45" r="35"/>
      <text class="label" x="55" y="50" text-anchor="middle">User</text>
      <circle class="node" cx="435" cy="45" r="35"/>
      <text class="label" x="435" y="50" text-anchor="middle">Service</text>
      <line x1="90" y1="40" x2="400" y2="40" stroke="var(--color-fast)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.3s" repeatCount="indefinite" />
      </line>
      <line x1="90" y1="50" x2="400" y2="50" stroke="var(--color-fast)">
        <animate attributeName="stroke-dashoffset" values="0;10" dur="0.3s" repeatCount="indefinite" />
      </line>
    </svg>

    <!-- Phase 2 -->
    <svg class="phase-svg phase-2" viewBox="0 0 490 90">
    <circle class="pulse" cx="245" cy="45" r="35"/>
      <circle class="node" cx="55" cy="45" r="35"/>
      <text class="label" x="55" y="50" text-anchor="middle">User</text>
      <circle class="node" cx="435" cy="45" r="35"/>
      <text class="label" x="435" y="50" text-anchor="middle">Service</text>
      <circle class="node proxy" cx="245" cy="45" r="35"/>
      <text class="label" x="227" y="40">
        fault
        <tspan x="222" dy="1.2em">↓300 ms</tspan>
      </text>
      <line x1="90" y1="40" x2="210" y2="40" stroke="var(--color-fast)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.2s" repeatCount="indefinite" />
      </line>
      <line x1="210" y1="50" x2="90" y2="50" stroke="var(--color-slow)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="1.3s" repeatCount="indefinite" />
      </line>
      <line x1="280" y1="40" x2="400" y2="40" stroke="var(--color-fast)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.2s" repeatCount="indefinite" />
      </line>
      <line x1="400" y1="50" x2="280" y2="50" stroke="var(--color-fast)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.2s" repeatCount="indefinite" />
      </line>
    </svg>

    <!-- Phase 3 -->
    <svg class="phase-svg phase-3" viewBox="0 0 490 90">
    <circle class="pulse" cx="245" cy="45" r="35"/>
      <circle class="node" cx="55" cy="45" r="35"/>
      <text class="label" x="55" y="50" text-anchor="middle">User</text>
      <circle class="node" cx="435" cy="45" r="35"/>
      <text class="label" x="435" y="50" text-anchor="middle">Service</text>
      <circle class="node proxy" cx="245" cy="45" r="35"/>
      <text class="label" x="227" y="40">
        fault
        <tspan x="218" dy="1.2em">↑blackhole</tspan>
      </text>
      <line x1="90" y1="40" x2="210" y2="40" stroke="var(--color-fast)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.3s" repeatCount="indefinite" />
      </line>
      <line x1="280" y1="40" x2="300" y2="40" stroke="var(--color-slow)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.2s" repeatCount="indefinite" />
      </line>
      <line x1="210" y1="50" x2="90" y2="50" stroke="var(--color-fast)" />
      <line x1="400" y1="50" x2="280" y2="50" stroke="var(--color-fast)" />
    </svg>

    <!-- Phase 4 -->
    <svg class="phase-svg phase-4" viewBox="0 0 490 90">
    <circle class="pulse" cx="245" cy="45" r="35"/>
      <circle class="node" cx="55" cy="45" r="35"/>
      <text class="label" x="55" y="50" text-anchor="middle">User</text>
      <circle class="node" cx="435" cy="45" r="35"/>
      <text class="label" x="435" y="50" text-anchor="middle">Service</text>
      <circle class="node proxy" cx="245" cy="45" r="35"/>
      <text class="label" x="227" y="35">
        fault
        <tspan x="218" dy="1.2em">↑512 Kbps</tspan>
        <tspan x="222" dy="1.2em">↓150 ms</tspan>
      </text>
      <line x1="90" y1="40" x2="210" y2="40" stroke="var(--color-fast)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.3s" repeatCount="indefinite" />
      </line>
      <line x1="210" y1="50" x2="90" y2="50" stroke="var(--color-slow)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="1s" repeatCount="indefinite" />
      </line>
      <line x1="280" y1="40" x2="400" y2="40" stroke="var(--color-slow)" class="thin">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.2s" repeatCount="indefinite" />
      </line>
      <line x1="400" y1="50" x2="280" y2="50" stroke="var(--color-fast)">
        <animate attributeName="stroke-dashoffset" values="10;0" dur="0.3s" repeatCount="indefinite" />
      </line>
    </svg>

  </div>
  
  </div>
</div>


  <div class="features-container">
    <div class="feat" data-images="proxy-run.png,inject-platform.png,proxy-sched.png,proxy-any.png,proxy-plugin.png">
      <div class="media">
        <img src="/assets/images/proxy-run.png" class="carousel-img">
      </div>
      <div class="menu">
        <span class="subtext">FAULT INJECTION MADE EASY</span>
        <h2 class="menu-heading">Reliability Driven Proxy</h2>
        <ul class="menu-list">
          <li class="menu-item active" data-index="0">
            <span><strong>Run locally</strong> and get immediate insights</span>
          </li>
          <li class="menu-item" data-index="1">
            <span><strong>Inject network faults</strong> into your platform resources</span>
          </li>
          <li class="menu-item" data-index="2">
            <span><strong>Mix multiple faults </strong> to create realistic scenarios</span>
          </li>
          <li class="menu-item" data-index="3">
            <span><strong>Explore all your layers</strong> and discover how your database or dependencies may impact
              your services</span>
          </li>
          <li class="menu-item" data-index="4">
            <span><strong>Make it your own</strong> by extending fault with gRPC plugins</span>
          </li>
        </ul>
      </div>
    </div>
    <div class="feat" data-images="scenario-generate.png,scenario-run.png,scenario-reporting.png,scenario-slo.png">
      <div class="media">
        <img src="/assets/images/scenario-generate.png" class="carousel-img">
      </div>
      <div class="menu">
        <span class="subtext">DESIGNED FOR DEVELOPERS & SRE</span>
        <h2 class="menu-heading">Reliability Engineering Automation</h2>
        <ul class="menu-list">
          <li class="menu-item active" data-index="0">
            <span><strong>Full API coverage</strong> with scenario automated creation</span>
          </li>
          <li class="menu-item" data-index="1">
            <span><strong>Think unit tests </strong> and hook into your favourite CI pipeline</span>
          </li>
          <li class="menu-item" data-index="2">
            <span><strong>Get insights</strong> from comprehensive & rich reports</span>
          </li>
          <li class="menu-item" data-index="3">
            <span><strong>Plug-in SLO</strong> to learn how users may be impacted as early as possible</span>
          </li>
        </ul>
      </div>
    </div>
    <div class="feat" data-images="scenario-review.png,code-review.png">
      <div class="media">
        <img src="/assets/images/scenario-review.png" class="carousel-img">
      </div>
      <div class="menu">
        <span class="subtext">FASTRACK RELIABILITY CHANGES</span>
        <h2 class="menu-heading">AI Agent For Reliability Engineers</h2>
        <ul class="menu-list">
          <li class="menu-item active" data-index="0">
            <span><strong>Get deeper analysis</strong> and enable the discussion with your team</span>
          </li>
          <li class="menu-item" data-index="1">
            <span><strong>Review your code </strong> and discover possible reliability-focused improvements</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>
