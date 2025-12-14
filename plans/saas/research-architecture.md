# SaaS Technical Architecture Research

**Research Date**: 2025-12-14
**Agent**: Agent 2 - Technical Architecture
**Purpose**: Foundational research for kgents SaaS platform architecture

---

## Table of Contents

1. [Multi-Tenant API Patterns](#1-multi-tenant-api-patterns)
2. [Usage Metering at Scale](#2-usage-metering-at-scale)
3. [Kubernetes Deployment for AI/ML Workloads](#3-kubernetes-deployment-for-aiml-workloads)
4. [Open Source Tools & Frameworks](#4-open-source-tools--frameworks)
5. [Security Best Practices](#5-security-best-practices)
6. [Architecture Recommendations](#6-architecture-recommendations)

---

## 1. Multi-Tenant API Patterns

### 1.1 Core Isolation Models

Modern SaaS architectures employ three primary tenant isolation strategies:

#### Pool Model (Shared Database)
**Description**: All tenants share the same database and tables with logical separation via tenant identifiers.

**Pros**:
- Optimal resource utilization and cost efficiency
- Operational simplicity with single database to manage
- Ideal for thousands of small tenants
- Lower infrastructure overhead

**Cons**:
- Complex isolation logic creates potential for data leakage
- "Noisy neighbor" problems require sophisticated rate limiting
- Requires careful query design to prevent tenant data mixing
- Higher security risk if isolation logic has bugs

**Best For**: High-volume, small-to-medium tenants with standard feature sets

#### Silo Model (Database-per-Tenant)
**Description**: Each tenant receives a dedicated database instance with complete physical separation.

**Pros**:
- Highest level of data isolation
- Ideal for regulated industries (healthcare, finance)
- Simplifies compliance with data residency requirements
- Easy per-tenant backup and restore
- Natural performance isolation

**Cons**:
- Higher infrastructure costs
- Increased operational complexity (managing hundreds/thousands of databases)
- More difficult to implement shared features
- Scaling challenges with database proliferation

**Best For**: Enterprise customers, regulated industries, high-value tenants

#### Hybrid Approach (Tiered Architecture)
**Description**: Combines pool and silo models with shared control plane and tiered data planes.

**Pros**:
- Shared control plane (auth, billing, APIs) for efficiency
- Standard customers share pooled infrastructure
- Enterprise customers get dedicated silos
- Natural upgrade path as customers grow
- Aligns infrastructure costs with revenue

**Cons**:
- Most complex to implement and maintain
- Requires sophisticated provisioning and orchestration
- Mixed operational patterns

**Best For**: SaaS platforms with diverse customer segments and pricing tiers

### 1.2 Database Isolation Strategies

#### Row-Level Security (RLS) with PostgreSQL

PostgreSQL's RLS feature (9.5+) provides automated query filtering at the database level:

**How It Works**:
- Security policies attached directly to tables
- Policies evaluate conditions for each row on access
- Enforcement happens before query results return
- Acts as an automated WHERE clause managed by the database

**Benefits**:
- Enhanced security: Harder to bypass through SQL injection
- Centralized control: Consistent policies across all services
- Simplified development: Developers write standard SQL
- Eases burden on application developers

**Implementation Approaches**:
1. **Database user per tenant**: Create unique DB user matching tenant identifier
2. **Shared user with session context**: Set configuration property on connection mapped to tenant ID

**Performance Considerations**:
- Row filtering can slow queries with millions of rows
- Mitigation: Proper indexing on tenant ID columns
- Use connection pooling efficiently
- Consider materialized views for complex queries

### 1.3 API Layer Best Practices

#### Tenant Context Management
- **Never trust client-provided tenant IDs**: Always derive tenant from authentication
- **Use database views/ORM scopes**: Auto-inject tenant filters
- **Validation at every boundary**: API, database, cache, background jobs
- **Add isolation tests to CI/CD**: Prevent regression

#### API Gateway Architecture
```
Edge → API Gateway → Services → PostgreSQL (RLS) → Object Storage → Queues → Observability
```

**Gateway Responsibilities**:
- Validate JWTs
- Enforce rate limits (per-tenant)
- Log all requests
- Route through PrivateLink to internal services

#### Quota and Metering
- **Meter key dimensions**: Users, API calls, storage GB, compute hours, premium features
- **Enforce at gateway/service layer**: Return clear errors and upgrade paths
- **Provide usage visibility**: Customer self-service portals

### 1.4 Cloud Platform Implementations

#### AWS Architecture
- **Compute**: EKS (Kubernetes), ECS (containers)
- **Database**: RDS/Aurora PostgreSQL with RLS
- **API Management**: API Gateway with Cognito/IAM
- **Observability**: CloudWatch
- **Provisioning**: CloudFormation, CDK, or Terraform

**AWS SaaS Builder Toolkit (SBT)**:
- Developer toolkit implementing SaaS best practices
- Handles tenant provisioning/deprovisioning
- Event-based integration with application plane
- Accelerates development with boilerplate abstractions

**Reference Architectures**:
- EKS Reference Architecture (with SBT integration)
- ECS Reference Architecture (supports Premium Tier silo model)
- Serverless SaaS Reference (Lambda-based)

### 1.5 Real-World Patterns

**Schema-per-Tenant (Medium Scale)**:
- Tenants share database but get separate schemas
- Logical separation within same physical database
- Balance between isolation and cost
- Requires efficient connection pooling and database routing

**Case Study Insight**:
- High tenant volume with variable usage → Schema-per-tenant with tenant-aware API rate limiting
- Large regulated tenants → Database-per-tenant with dedicated VPCs
- Small/standard tenants → Pool model with RLS and strict quota enforcement

---

## 2. Usage Metering at Scale

### 2.1 Key Trends (2025)

- **Usage-based pricing dominance**: Preferred by majority of SaaS buyers
- **AI-native product design**: Token-based billing for LLM APIs
- **Revenue infrastructure modernization**: Moving from flat pricing to dynamic models
- **Real-time metering**: Customers expect immediate usage visibility

### 2.2 Essential Metering Capabilities

#### Granular Usage Tracking
- **Track everything billable**: API calls, tokens, compute hours, storage
- **Differentiate usage types**: Internal, partner, third-party
- **Micro-usage aggregation**: Precise tracking even for small units
- **Multi-dimensional metering**: Combine metrics (tokens + API calls + users)

#### Real-Time vs. Batch Processing
- **Real-time tracking**: Critical for cloud-based API services
- **Prevents revenue leakage**: Capture all usage without gaps
- **Consistent reporting**: Same data for business and customers

### 2.3 Implementation Best Practices

#### 1. Customer Self-Service Portals
- Customers monitor their own usage in real-time
- Prevents bill shock and unexpected overages
- Promotes billing transparency and trust
- Enables proactive cost management

#### 2. Define Clear Value Metrics
- Align pricing with customer value (API calls, compute hours, active users)
- Enable pricing changes without engineering work
- Run simulations on historical data
- Optimize for customer value delivery

#### 3. Track Essential Metrics
- **API DAU/MAU**: Unique consumers of API
- **Response time**: Performance indicators
- **Error rates**: Quality metrics
- **Usage patterns**: Peak times, growth trends

#### 4. Rate Limiting Integration
- **Algorithms**: Fixed Window, Sliding Window, Token Bucket, Leaky Bucket
- **Dynamic adjustment**: Monitor metrics and adjust limits
- **Track patterns**: Request frequency, peak usage, growth

### 2.4 Rate Limiting Algorithms

#### Token Bucket Algorithm

**How It Works**:
- Maintains bucket refilled at fixed rate
- Each request consumes one token
- Requests denied when bucket empty
- Allows traffic bursts when bucket has tokens

**Pros**:
- Memory efficient
- Allows controlled bursts
- Good for variable traffic patterns

**Cons**:
- Complex in distributed systems
- Race conditions require careful handling
- Requires clock synchronization

**Use Case**: APIs with bursty traffic (login spikes, product launches)

#### Leaky Bucket Algorithm

**How It Works**:
- Bucket processes requests at constant rate
- Requests queue up in bucket
- Overflow requests are rejected
- Smooths out traffic bursts

**Pros**:
- Predictable output rate
- Smooths traffic flow
- Ideal for downstream rate limits

**Cons**:
- Can slow down queries with high load
- Less flexible for bursts
- May reject valid requests during spikes

**Use Case**: Streaming services, payment processing (steady flow required)

#### Sliding Window Counter

**How It Works**:
- Combines fixed window with weighted average
- More accurate than fixed window
- Balances accuracy with resource usage

**Pros**:
- Prevents fixed window boundary issues
- More accurate rate limiting
- Good for mixed traffic patterns

**Cons**:
- Higher computational overhead
- More complex implementation

**Use Case**: General-purpose API rate limiting

#### Redis Implementation
```python
# Token Bucket with Redis (Atomic Operations via Lua)
# Retrieve current token count and last refill time
# Calculate tokens to add based on time elapsed
# Update token count and process request
# Use MULTI/EXEC for atomicity
```

**Key Considerations**:
- Use Lua scripts for atomic operations
- Avoid race conditions in distributed environments
- Optimize for space with Redis hashes
- Consider GCRA (Generic Cell Rate Algorithm) for simplicity

### 2.5 Billing Model Options

#### Pure Usage-Based
- Bill entirely on consumption
- Aligns with customer value
- Variable revenue (pro/con)

#### Hybrid Model
- Fixed base charge + usage metering
- Predictable revenue baseline
- Flexibility for customers
- Reduces churn from bill shock

#### Tiered Pricing
- Volume discounts for higher usage
- Encourages growth and expansion
- Common pricing: $0.01 per 1,000 tokens

### 2.6 Token Consumption Metering for AI APIs

#### Why Token Metering Matters
- LLMs charge by tokens, GPU hours, inference calls
- Infrastructure bills scale with compute, not headcount
- Flat subscription + variable costs = margin erosion
- Single active customer can trigger hundreds in inference costs

#### Technical Architecture
```
API → Event Listener → NATS (message broker) → Metering Service → Billing System
```

**Components**:
- **API**: Tracks token consumption per user
- **Event Listener**: Chronicles token-related activities
- **Message Broker**: Real-time communication channel (NATS, Kafka)
- **Metering Service**: Aggregates and sends to billing

#### Pricing Models for AI
- **Pay-as-you-go**: $0.01 per 1,000 tokens
- **Tiered pricing**: Discounts for volume
- **Separate input/output pricing**: Different rates based on processing costs (OpenAI model)

#### Challenges
- **Data consistency**: Metrics systems may lose data or double-count
- **Idempotency required**: Ensure usage counted exactly once
- **Real-time visibility**: Customers need cost predictions
- **High-volume ingestion**: Process 200,000+ events/second

### 2.7 Implementation Tools

#### API Gateway Built-in Analytics
- AWS API Gateway
- Google Apigee
- Kong Gateway
- Track basic metrics out of the box

#### Specialized Analytics Platforms
- Moesif: Deep business-oriented metrics
- Segment: Customer data platform
- Datadog API Analytics: Full-stack observability

#### Advantages of Specialized Tools
- More business context than gateway-level analytics
- Developer engagement tracking
- Custom metric aggregation
- Integration with billing systems

### 2.8 AWS Marketplace Best Practices
- Report usage for previous hour
- Use AWS CloudTrail for audit verification
- Ensure accurate records over time
- Configure metering for SaaS subscriptions

---

## 3. Kubernetes Deployment for AI/ML Workloads

### 3.1 Current State (2025)

**Adoption Statistics**:
- 48% of organizations use Kubernetes for AI/ML workloads
- GPU acceleration: 10-100x performance improvement over CPU
- Training large language models: Thousands of GPU hours
- "Kubernetes AI" search volume: 300% increase in 2025

**Key Challenge**: Kubernetes has pod-centric scheduler, but AI workloads care about GPU count, type, and topology.

### 3.2 Core GPU Scheduling Challenges

**Scheduler Limitations**:
- Default scoring and fit predicates insufficient
- Doesn't coordinate multi-GPU, multi-node setups
- Network topology not considered
- Tenant quotas require external tools

**Resource Utilization**:
- GPU utilization in inference: Often only 10-30%
- GPU nodes are expensive: Requires intelligent autoscaling
- Need for GPU sharing and partitioning

### 3.3 GPU Scheduling Patterns and Solutions

#### 1. Gang Scheduling with Kueue and Volcano

**Kueue**:
- Adds admission control layer before pod scheduling
- Workloads enqueue into LocalQueues → bind to ClusterQueues
- Simulates scheduling across cluster
- Admits entire workload (gang) or keeps pending
- Cohorts allow queues to borrow idle quota with weighted fairness

**Benefits**:
- All-or-nothing scheduling for distributed training
- Fair sharing across teams
- Quota management
- Works on AKS, EKS, GKE

**Volcano**:
- Specialized batch scheduler for Kubernetes
- Gang scheduling for batch jobs
- Queue management
- Better than default scheduler for ML workloads

#### 2. GPU Sharing and Partitioning

**Time-Slicing**:
- Multiple pods share GPU by rapid switching
- Good for inference and small training workloads
- Increases utilization from 10-30% to 60-80%

**MIG (Multi-Instance GPU)**:
- NVIDIA A100/H100 feature
- Partition single GPU into isolated instances
- Hardware-level isolation
- Each instance has dedicated memory and compute

**MPS (Multi-Process Service)**:
- NVIDIA feature for GPU sharing
- Multiple processes share GPU concurrently
- Software-level sharing
- Lower overhead than time-slicing

**Recommendation**:
- Serving and small training: MIG or MPS
- Large training jobs: Reserve full GPUs
- Inference with low utilization: Time-slicing

#### 3. NVIDIA GPU Operator

**Default for Production (2025)**:
- Installs drivers, nvidia-container-toolkit, DCGM, device plugin
- Automates GPU node setup on Kubernetes

**Workflow**:
1. **Discovery**: Identify nodes with GPUs
2. **Installation**: Containerized drivers, Container Toolkit, device plugin
3. **Validation**: Ensure proper configuration before scheduling
4. **Reliability**: Prevents misconfigured nodes from disrupting workloads

**Benefits**:
- Consistent GPU environment across nodes
- Automated lifecycle management
- Reduces operational complexity

### 3.4 Advanced Autoscaling for GPU Workloads

#### Cluster Autoscaler
- Provision GPU nodes when training/inference pods pending
- Scale down during idle periods
- Minimize costs for expensive GPU nodes

#### KEDA (Kubernetes Event-Driven Autoscaling)
- Combine with NVIDIA DCGM metrics
- Scale GPU node pools based on real-time utilization
- Scale to zero when no workloads running
- Supports custom metrics from inference servers

#### Horizontal Pod Autoscaler (HPA)
- Watch CPU or GPU usage
- Spin up new pods during high load
- Essential for unpredictable inference workloads
- Best practice: Monitor custom metrics (queue depth, latency)

### 3.5 Kubernetes AI Conformance Program

**Program Overview**:
- Defines standard capabilities for AI/ML on Kubernetes
- Builds on CNCF Certified Kubernetes Conformance
- Azure AKS among first certified platforms

**Standard Capabilities**:
- APIs for GPU scheduling
- Configurations for AI workloads
- Reliability and efficiency guarantees

**Significance**: Ensures consistent AI deployment experience across cloud providers

### 3.6 ML Platform Frameworks

#### Kubeflow
**Description**: Kubernetes-native platform for deploying, scaling, managing AI.

**Key Components**:
- **Kubeflow Trainer**: LLM fine-tuning with PyTorch, HuggingFace, DeepSpeed, MLX, JAX, XGBoost
- **KServe**: Standardized inference platform (covered in section 4.4)
- **Kubeflow Pipelines (KFP)**: Build and deploy ML workflows

**Pros**:
- End-to-end ML orchestration
- Multi-user environment support
- Native Kubernetes integration
- Comprehensive ecosystem

**Cons**:
- High complexity
- Requires Kubernetes expertise
- Can be overkill for smaller teams

**Best For**: Organizations with existing Kubernetes expertise needing robust ML orchestration

#### MLflow
**Description**: Lightweight experiment tracking, model versioning, deployment.

**Key Features**:
- Created by Databricks
- Simple and intuitive
- Easy integration with other frameworks
- Widely used for experiment tracking

**Integration**: Works with Ray Train and Tune, Weights & Biases

#### Ray and KubeRay
**Description**: Open-source framework for scaling complex AI workloads.

**Ray Features**:
- Distributed training and serving
- Simple and intuitive API
- Heavily used for AI and Python applications
- Handles complex workload orchestration

**KubeRay**:
- Toolkit for deploying Ray on Kubernetes
- Ray is not Kubernetes-native, KubeRay bridges the gap
- Enables Prometheus metrics integration
- Grafana visualization support

**Benefits**:
- Cost savings: Scale based on demand
- Easy observability with Prometheus/Grafana
- Distributed computing across ML lifecycle

#### Combined Platform Strategy
**Kubeflow + Ray**:
- Kubeflow: Multi-user environment, notebook management
- Ray: Distributed computing for training and serving
- Kubernetes: Scalable infrastructure

**Optimization**:
- Combine CPU and GPU instances in same cluster
- Optimize for cost and performance
- Distributed training for large models

### 3.7 Best Practices Summary

#### Cultural Shift
Treat GPUs as shared, policy-driven substrate governed by queues, not as pets assigned to projects.

#### GPU-Aware Primitives
- Device plugins for GPU discovery
- MIG and MPS for GPU sharing
- Gang admission for distributed training
- Quotas and cohorts for multi-tenancy
- Preemption aligned with business priorities

#### Resource Management
- Set appropriate CPU, memory, GPU requests and limits
- Use node affinity for hardware placement
- Use taints/tolerations for GPU nodes
- Monitor and optimize GPU utilization

#### Cost Optimization
- Scale to zero when possible
- Use spot instances for training
- Reserve instances for production inference
- Right-size GPU types for workload

---

## 4. Open Source Tools & Frameworks

### 4.1 Multi-Tenant API Gateways

#### Kong Gateway
**License**: Apache 2.0 (open source)

**Overview**:
- Built on Nginx HTTP proxy server
- Written in Lua scripting language
- Released 2011, mature ecosystem

**Multi-Tenancy Features**:
- Flexible plugin architecture
- Consumer and credential constructs for tenant isolation
- Seamless Kubernetes integration
- Per-consumer rate limiting
- Dedicated Gateway instances for high-priority tenants

**Capabilities**:
- Logging, authentication, rate limiting
- Failure detection and circuit breaking
- CLI for command-line management
- Large plugin ecosystem

**Pros**:
- Permissive Apache 2.0 license
- Strong community and commercial support
- Extensive documentation
- Production-proven at scale

**Cons**:
- Lua learning curve
- Plugin complexity for advanced features
- Resource overhead with many plugins

**Best For**: Organizations needing flexible, production-grade API management

#### Tyk Gateway
**License**: MPL (Mozilla Public License) - less permissive than Apache 2.0

**Overview**:
- Cloud-native, open source
- Written in Go (better performance claims)
- Batteries-included approach

**Key Features**:
- Authentication out of the box: OIDC, OAuth2, Bearer Token, Basic Auth, Mutual TLS, HMAC
- No plugins required for standard features
- Higher throughput (Go-based claims)
- Developer-friendly

**Pros**:
- Fully open source without paywalls
- Simpler than Kong for common use cases
- Modern, lightweight architecture
- Built-in features reduce plugin dependency

**Cons**:
- MPL license restrictions
- Smaller ecosystem than Kong
- Less mature plugin system

**Best For**: Teams wanting batteries-included gateway without plugin complexity

#### Emissary-Ingress (Ambassador)
**Type**: CNCF open source project

**Overview**:
- Kubernetes-native API Gateway
- Built on Envoy Proxy
- Formerly known as Ambassador API Gateway

**Key Features**:
- Designed explicitly for Kubernetes
- Declarative configuration (Kubernetes annotations, YAML)
- Deep integration with Kubernetes ecosystem
- Can work with Istio for service mesh

**Pros**:
- Native Kubernetes integration
- CNCF backing
- Envoy Proxy benefits (observability, resilience)
- Modern cloud-native architecture

**Cons**:
- Kubernetes-only (not for non-K8s environments)
- Less flexible outside Kubernetes
- Smaller community than Kong/Tyk

**Best For**: Kubernetes-native organizations, microservices architectures

#### Multi-Tenant Optimization Features (All Gateways)
- Per-tenant rate limits based on credentials
- Quota enforcement over time
- Tenant-specific policies (IP whitelisting, JWT validation)
- Plugin architectures for custom logic
- Request/response transformations

### 4.2 Usage Metering and Billing Platforms

#### Lago
**License**: Open source (self-hosted free, cloud version paid)
**Repository**: https://github.com/getlago/lago

**Overview**:
- Open source alternative to Chargebee, Recurly, Stripe Billing
- Supports usage-based, subscription-based, hybrid pricing
- Y Combinator backed

**Key Features**:
- Event-based architecture: "If you can track it, you can charge for it"
- Ingest up to 15,000 billing events per second
- Composable design: Connects to payment gateways, CRM, CPQ, accounting software
- Subscription management and pricing iterations
- Payment orchestration
- Revenue analytics

**Deployment Options**:
- Self-hosted (free): Your data never leaves infrastructure
- Cloud version: Priced like SaaS

**Pros**:
- True open source with self-hosting
- High-volume event ingestion
- Comprehensive feature set
- Active development and community

**Cons**:
- Newer than Kill Bill (less battle-tested)
- Requires infrastructure setup for self-hosting
- Cloud version has costs

**Best For**: Teams wanting self-hosted billing with modern architecture

#### OpenMeter
**License**: Open source + managed cloud
**Website**: https://openmeter.io

**Overview**:
- Real-time usage metering system evolved into billing platform
- Designed for AI and DevTool companies
- High-throughput event tracking

**Technical Architecture**:
- Kafka + ClickHouse backbone
- Handles millions of events per second
- Real-time processing

**Key Features**:
- Product catalogs
- Entitlements (feature access and usage limits)
- Subscriptions and invoicing
- Plan versioning
- SDKs: Node.js, Python, Go
- Integrations: Stripe for payments, CRMs, tax providers

**Pros**:
- Highest throughput (Kafka + ClickHouse)
- Modern, scalable architecture
- Open source + cloud options
- Strong AI/ML use case support

**Cons**:
- Focused on metering, pairs with Stripe for payments
- Newer platform (smaller community)
- Requires understanding of event-driven architecture

**Best For**: High-volume API platforms, AI startups, DevTool companies

#### Kill Bill
**License**: Open source (Apache 2.0)
**Overview**: Battle-tested subscription billing with deep plugin ecosystem

**Key Features**:
- Infrastructure-grade billing
- Reliable and auditable
- Endlessly customizable
- Enterprise multi-product billing
- Cross-region support

**Pros**:
- Mature and battle-tested
- Deep plugin ecosystem
- Enterprise-grade reliability
- Strong audit capabilities

**Cons**:
- Java-based (enterprise skew)
- Heavy setup costs
- Requires significant engineering resources
- Complex for simple use cases

**Best For**: Enterprise organizations with complex billing needs across regions

#### Comparison Summary
- **Lago**: Modern, self-hostable, best for general SaaS
- **OpenMeter**: Highest throughput, best for AI/ML APIs
- **Kill Bill**: Enterprise-grade, best for complex multi-product billing

### 4.3 AI/ML Platform Tools

#### Kubeflow
**Type**: CNCF project
**Website**: https://www.kubeflow.org

**Components**:
- Kubeflow Trainer: LLM fine-tuning
- KServe: Model serving
- Kubeflow Pipelines: Workflow orchestration
- Notebooks: JupyterHub integration

**Pros**:
- Comprehensive end-to-end platform
- Kubernetes-native
- Strong community

**Cons**:
- Complex setup
- Steep learning curve
- Requires Kubernetes expertise

#### MLflow
**Owner**: Databricks
**Focus**: Experiment tracking, model registry

**Pros**:
- Simple and lightweight
- Wide adoption
- Framework-agnostic

**Cons**:
- Limited orchestration
- Requires additional tools for production deployment

#### Ray + KubeRay
**Type**: Open source
**Focus**: Distributed computing for AI

**Pros**:
- Scales complex workloads easily
- Simple API
- Production-ready

**Cons**:
- Not Kubernetes-native (needs KubeRay)
- Learning curve for distributed programming

### 4.4 AI Model Serving Platforms

#### KServe
**Type**: CNCF incubating project
**Repository**: https://github.com/kserve/kserve

**Overview**:
- Standardized distributed generative and predictive AI inference platform
- Kubernetes-native
- v0.15+ has first-class generative AI support

**Key Features**:
- Serverless inference with Knative (scale-to-zero)
- KEDA integration for custom metrics
- Multi-framework support
- Rapid scaling based on traffic

**Pros**:
- CNCF backing and strong community
- Serverless capabilities reduce costs
- Flexible and scalable
- LLM optimization in v0.15+

**Cons**:
- Requires Kubernetes expertise
- Overkill for simple serving
- Complex setup

**Best For**: Kubernetes teams, serverless ML serving, LLM deployment

#### Seldon Core
**License**: Business Source License (BSL) 1.1 (as of Jan 2024, previously open source)
**Overview**: MLOps framework for deploying, scaling, monitoring models

**Key Features**:
- Microservice graph of model components
- Inference pipelines with multiple steps (chaining models, transformers, routers)
- A/B testing of model versions
- Shadow deployments and canary rollouts
- Explainers and outlier detectors

**Pros**:
- Production rollout features (A/B, canary, shadow)
- Complex inference graphs
- Mature ecosystem

**Cons**:
- No longer fully open source (BSL 1.1)
- License restrictions for commercial use
- More complex than alternatives

**Best For**: Large-scale production with advanced deployment patterns

#### BentoML
**License**: Open source
**Website**: https://www.bentoml.com

**Overview**:
- Flexible, developer-friendly framework
- Package and deploy models as microservices
- High-performance API model server

**Key Features**:
- Supports all major ML frameworks (TensorFlow, PyTorch, XGBoost, scikit-learn)
- Adaptive micro-batching
- Beginner-friendly

**Pros**:
- Easy to use
- Fast development iteration
- Good documentation
- Open source

**Cons**:
- No native Kubernetes support (requires external tools)
- No built-in monitoring/scaling
- Less enterprise features

**Best For**: Startups, small teams, fast-moving ML projects

#### Model Serving Recommendation Matrix
- **Startups/Small Teams**: BentoML (ease of use)
- **Kubernetes Organizations**: KServe (serverless, scale-to-zero)
- **Enterprise Production**: Seldon Core (advanced features) or KServe (if avoiding BSL)
- **LLM Deployment (2025)**: KServe v0.15+ (generative AI optimizations)

### 4.5 Observability Stack

#### Prometheus
**Type**: Open source metrics collection
**Overview**: Industry-standard metrics system with alerting

**Features**:
- Pull-based metrics collection
- Time-series database
- PromQL query language
- Alerting with Alertmanager

**Pros**:
- De facto standard for Kubernetes
- Rich ecosystem
- Powerful query language

**Cons**:
- Pull model challenging for ephemeral workloads
- Requires Pushgateway for short-lived jobs
- Limited long-term storage (needs remote storage)

#### Grafana
**Type**: Open source visualization
**Overview**: Powerful dashboards and alerting platform

**Features**:
- Multi-source data (Prometheus, ClickHouse, PostgreSQL)
- Beautiful dashboards
- Alerting and notifications
- AI Observability integration (2025)

**AI-Specific Features (Grafana Cloud)**:
- LLM response time, throughput, availability tracking
- Cost management and spend tracking
- Token consumption analytics
- GPU utilization, thermal management
- VectorDB performance monitoring
- MCP (Model Context Protocol) observability

**Integrations**:
- OpenLIT SDK for AI observability
- Anthropic Claude usage dashboards
- OpenAI monitoring
- Custom AI metrics

#### Combined Stack Best Practices
- Prometheus for metrics collection
- Grafana for visualization
- Push metrics from ephemeral workloads to Pushgateway
- Use prebuilt dashboards for common services
- Set up alerting for SLOs
- Monitor AI-specific metrics (tokens, costs, GPU utilization)

---

## 5. Security Best Practices

### 5.1 OWASP Cloud Tenant Isolation

**Project Goal**: Create practical guidance for cloud developers to manage isolation escape risks and mitigate cross-tenant vulnerabilities.

**Cross-Tenant Vulnerabilities**: New security risk class for cloud applications where malicious tenants break security boundaries and access other tenants' data.

### 5.2 Common Security Mistakes

OWASP identifies these common mistakes enabling cross-tenant vulnerabilities:

1. **Misconfigured containers**: Improper isolation settings
2. **Overly permissive firewall rules**: Cross-tenant network access
3. **Lack of data hygiene**: Tenant data not properly tagged
4. **Insufficient access control**: Missing authorization checks
5. **Shared resource vulnerabilities**: Improper isolation of shared services

### 5.3 Real-World Examples

**Tenable (Azure)**:
- Insufficient access control
- Potential unauthorized access to cross-tenant applications
- Sensitive data exposure (including authentication secrets)

**Orca Security (AWS Glue)**:
- Critical security misconfiguration
- Attacker could create resources in other customers' accounts
- Access data of other AWS Glue customers

### 5.4 Key Security Best Practices

#### Access Control
- **Tenant Isolation**: Enforce strict logical separation to prevent data leakage
- **Granular Access Controls**: Users access only permitted resources within tenant
- **Clear Ownership Boundaries**: Define resource ownership in tenant context
- **Never trust client-provided tenant IDs**: Always derive from authentication

#### Isolation Models
**Silo Isolation**:
- Resources fully isolated from other tenants
- No shared resources
- Highest security level
- Higher cost

**Pool Isolation**:
- Tenants share resources in unified environment
- Isolation via authentication policies
- Lower cost, requires careful implementation
- Higher risk if not properly configured

#### Data Isolation
**Logical Separation**:
- Database schemas, table partitioning, or separate databases
- Independent storage and access per tenant
- RLS policies for automated enforcement

**Encryption**:
- Strong encryption for data at rest and in transit
- Tenant-specific encryption keys
- Extra security layer

**Access Control**:
- Robust identity and access management
- Role-based access control (RBAC)
- Granular permission management

**Network Segmentation**:
- Virtual Private Networks (VPNs)
- Virtual Local Area Networks (VLANs)
- Isolated network segments per tenant

**Containerization**:
- Docker or Kubernetes for isolated environments
- Per-tenant application and data isolation
- Resource limits and namespaces

#### Defense in Depth
- Access control at every layer
- Fine-grained RBAC across authentication/authorization layers
- AWS: IAM policies
- Kubernetes: Native RBAC
- Application: Custom authorization logic

#### Auditing and Monitoring
- Comprehensive logging for all access attempts
- Track data modifications
- Monitor potential security incidents
- Regular security audits
- Identify and address vulnerabilities proactively

#### Testing Multi-Tenant Applications
- Use OWASP ZAP for vulnerability identification
- Configure for multi-tenant specific challenges
- Test tenant isolation boundaries
- Verify authorization at all layers

---

## 6. Architecture Recommendations

### 6.1 Recommended Architecture for kgents SaaS

Based on the research, here's a recommended technical architecture:

#### Tenant Isolation Strategy
**Hybrid Tiered Approach**:
- **Pool Model** (Standard Tier): Shared PostgreSQL with RLS for small/medium customers
- **Silo Model** (Enterprise Tier): Database-per-tenant for large/regulated customers
- **Shared Control Plane**: Single API layer, authentication, billing, admin UI

**Benefits**:
- Cost-efficient for standard customers
- Compliant and secure for enterprise customers
- Natural upgrade path as customers grow

#### API Layer
**API Gateway**: Kong (Apache 2.0, mature ecosystem)
- Per-tenant rate limiting
- JWT validation
- Usage metering hooks
- Plugin ecosystem for extensibility

**Alternative**: Tyk (if preferring batteries-included Go-based gateway)

#### Database Layer
**Primary**: PostgreSQL 15+ with Row-Level Security
- Shared database for pool tenants
- Schema-per-tenant for medium customers
- Database-per-tenant for enterprise (automated provisioning)
- Connection pooling (PgBouncer or built-in)

#### Usage Metering & Billing
**Metering**: OpenMeter (open source, high-throughput)
- Real-time token consumption tracking
- API call metering
- Kafka + ClickHouse for millions of events/second
- Customer usage dashboards

**Billing**: Lago (open source, self-hosted)
- Flexible pricing models (usage, subscription, hybrid)
- Integration with Stripe for payments
- Self-hosted for data sovereignty

**Alternative**: Use Stripe Billing directly if preferring managed service

#### Kubernetes Infrastructure
**Container Orchestration**: EKS (AWS), AKS (Azure), or GKE (Google Cloud)
- SaaS Builder Toolkit (if AWS) for tenant lifecycle
- Namespace-per-tenant for isolation
- GPU node pools for AI workloads

**GPU Scheduling**:
- NVIDIA GPU Operator for driver management
- Kueue for gang scheduling and quotas
- KEDA for autoscaling based on usage
- Time-slicing for inference workloads (increase GPU utilization)

#### AI/ML Deployment
**Experiment Tracking**: MLflow
- Simple, lightweight
- Track experiments during development

**Model Serving**: KServe
- Serverless inference with Knative
- Scale-to-zero for cost savings
- LLM optimization (v0.15+)
- Multi-framework support

**Distributed Training**: Ray + KubeRay
- Scale complex AI workloads
- Distributed training for large models
- Integration with MLflow for tracking

#### Observability
**Metrics**: Prometheus
- Scrape metrics from all services
- Custom metrics for AI workloads (token usage, GPU utilization)

**Visualization**: Grafana Cloud (with AI Observability)
- LLM cost tracking
- Token consumption analytics
- GPU performance monitoring
- Infrastructure metrics

**Logging**: ELK Stack or Grafana Loki
- Centralized logging
- Tenant-aware log routing

**Tracing**: Jaeger or Grafana Tempo
- Distributed tracing
- Performance debugging

#### Security
**Authentication**: Auth0 or Clerk
- Multi-tenant support out of the box
- SSO for enterprise customers
- RBAC integration

**Network Security**:
- Network policies in Kubernetes
- Private networking for inter-service communication
- WAF (Web Application Firewall) at edge

**Data Security**:
- PostgreSQL RLS for application-level isolation
- Encryption at rest (database and object storage)
- Encryption in transit (TLS everywhere)
- Tenant-specific encryption keys for enterprise tier

**Compliance**:
- Regular OWASP ZAP scans
- Automated security testing in CI/CD
- Audit logging for all tenant operations
- Penetration testing for multi-tenant boundaries

### 6.2 Technology Stack Summary

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **API Gateway** | Kong or Tyk | Mature, open source, multi-tenant features |
| **Database** | PostgreSQL 15+ with RLS | Industry standard, excellent RLS support |
| **Metering** | OpenMeter | High throughput, open source, AI-focused |
| **Billing** | Lago or Stripe | Flexible pricing models, self-hostable option |
| **Container Platform** | EKS/AKS/GKE | Managed Kubernetes, GPU support |
| **GPU Management** | NVIDIA GPU Operator + Kueue | Production standard, efficient scheduling |
| **Model Serving** | KServe | CNCF project, serverless, LLM support |
| **Experiment Tracking** | MLflow | Simple, widely adopted |
| **Distributed Compute** | Ray + KubeRay | Scale AI workloads, strong ecosystem |
| **Metrics** | Prometheus | De facto standard, rich ecosystem |
| **Visualization** | Grafana Cloud | AI observability, powerful dashboards |
| **Authentication** | Auth0 or Clerk | Multi-tenant SSO, RBAC |
| **Logging** | Grafana Loki | Cost-effective, Kubernetes-native |
| **Tracing** | Grafana Tempo | Integrated with Grafana stack |

### 6.3 Implementation Phases

#### Phase 1: Foundation (Months 1-2)
- Set up Kubernetes cluster (EKS/AKS/GKE)
- Deploy PostgreSQL with RLS
- Implement API gateway (Kong/Tyk)
- Basic authentication (Auth0/Clerk)
- Simple usage metering (Prometheus metrics)

#### Phase 2: Metering & Billing (Months 2-3)
- Deploy OpenMeter for real-time metering
- Integrate Lago for billing
- Implement customer usage dashboards
- Set up rate limiting per tenant
- Stripe payment integration

#### Phase 3: AI/ML Infrastructure (Months 3-4)
- Configure GPU node pools
- Deploy NVIDIA GPU Operator
- Implement KServe for model serving
- Set up MLflow for experiment tracking
- Configure Kueue for GPU scheduling

#### Phase 4: Observability & Security (Month 4-5)
- Full Prometheus + Grafana stack
- AI-specific dashboards (tokens, costs, GPU)
- Security scanning (OWASP ZAP)
- Audit logging
- Compliance documentation

#### Phase 5: Enterprise Features (Month 5-6)
- Database-per-tenant provisioning
- SSO for enterprise customers
- Advanced tenant isolation
- Custom encryption keys
- SLA monitoring

### 6.4 Cost Optimization Strategies

1. **GPU Utilization**:
   - Time-slicing for inference (share GPUs across tenants)
   - Scale-to-zero with KServe for idle models
   - Spot instances for training workloads
   - Right-size GPU types (T4 for inference, A100 for training)

2. **Database**:
   - Connection pooling to reduce overhead
   - Read replicas for read-heavy workloads
   - Automated backups with retention policies
   - Compress old data to cheaper storage

3. **Compute**:
   - Kubernetes autoscaling (HPA, VPA, Cluster Autoscaler)
   - Reserved instances for baseline capacity
   - Spot instances for batch workloads
   - Right-size node pools

4. **Observability**:
   - Metric retention policies
   - Sampling for high-volume traces
   - Log aggregation and filtering
   - Archive old logs to object storage

---

## Sources

### Multi-Tenant API Patterns
- [Multi-Tenant Architecture: The Complete Guide for Modern SaaS and Analytics Platforms](https://bix-tech.com/multi-tenant-architecture-the-complete-guide-for-modern-saas-and-analytics-platforms/)
- [Multi‑Tenant SaaS Architecture on Cloud (2025) — Practical Guide](https://isitdev.com/multi-tenant-saas-architecture-cloud-2025/)
- [How to Build & Scale a Multi-Tenant SaaS Application](https://acropolium.com/blog/build-scale-a-multi-tenant-saas/)
- [Multi-Tenant ASP.NET Core SaaS Applications: Architecture Patterns that Scale](https://medium.com/@syed.zeeshan.ali.jafri_99339/multi-tenant-asp-net-core-saas-applications-architecture-patterns-that-scale-b1ad766ac8c4)
- [Secure by Design: Architecture Patterns for Multi-Tenant SaaS at Scale](https://dev.to/niranjan_sharma_579448819/secure-by-design-architecture-patterns-for-multi-tenant-saas-at-scale-4bah)
- [How to Design a Multi-Tenant SaaS Architecture](https://clerk.com/blog/how-to-design-multitenant-saas-architecture)
- [Multi-Tenant Architecture - SaaS App Design Best Practices](https://relevant.software/blog/multi-tenant-architecture/)

### Database Isolation
- [Multi-tenant data isolation with PostgreSQL Row Level Security | AWS Database Blog](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/)
- [Multi-Tenant Data Isolation and Row Level Security](https://dzone.com/articles/multi-tenant-data-isolation-row-level-security)
- [Multi-tenancy implementation with PostgreSQL](https://blog.logto.io/implement-multi-tenancy)
- [Ensuring Tenant Data Isolation in Multi-Tenant SaaS Systems](https://www.tenupsoft.com/blog/strategies-for-tenant-data-isolation-in-multi-tenant-based-saas-applications.html)
- [Tenant isolation in multi-tenant systems | WorkOS](https://workos.com/blog/tenant-isolation-in-multi-tenant-systems)
- [SaaS Tenant Isolation Strategies: Database, Schema & Row-Level Security Explained](https://kodekx-solutions.medium.com/saas-tenant-isolation-database-schema-and-row-level-security-strategies-7337d2159066)
- [Achieving Robust Multi-Tenant Data Isolation with PostgreSQL Row-Level Security](https://leapcell.io/blog/achieving-robust-multi-tenant-data-isolation-with-postgresql-row-level-security)

### Usage Metering & Billing
- [Usage Metering for SaaS Billing: How it is a Game Changer](https://www.subscriptionflow.com/2025/09/usage-metering-for-saas-billing-how-it-is-redefining-payment-versatility/)
- [15 top SaaS trends & opportunities for 2025 you should know | Orb](https://www.withorb.com/blog/saas-trends)
- [13 API Metrics That Every Platform Team Should be Tracking | Moesif Blog](https://www.moesif.com/blog/technical/api-metrics/API-Metrics-That-Every-Platform-Team-Should-be-Tracking/)
- [Configuring metering for usage with SaaS subscriptions - AWS Marketplace](https://docs.aws.amazon.com/marketplace/latest/userguide/metering-for-usage.html)
- [API Usage Analytics: Understanding Importance and Implementation for SaaS Success](https://www.getmonetizely.com/articles/api-usage-analytics-understanding-importance-and-implementation-for-saas-success)
- [10 Best Practices for API Rate Limiting in 2025](https://dev.to/zuplo/10-best-practices-for-api-rate-limiting-in-2025-358n)
- [Usage Based Billing for API Products Explained](https://www.subscriptionflow.com/2025/07/usage-based-billing-for-api-products/)

### Token Consumption & AI Billing
- [OpenMeter - Fastest Way to Ship Usage-Based Billing, Metering](https://openmeter.io/use-cases/ai)
- [How to Implement Scalable Usage-Based Billing for AI Workloads](https://www.cloudraft.io/blog/usage-based-billing-for-ai-workloads)
- [Monetizing a Gen-AI-Based ChatBot API by Metering Token Usage | Moesif Blog](https://www.moesif.com/blog/technical/gen-ai/ChatBot-API-OpenAI-Token-Usaged-Based-Monetization/)
- [Best Open Source Usage-Based Billing Platform for an AI Startup (2025 Guide)](https://flexprice.io/blog/best-open-source-usage-based-billing-platform-for-an-ai-startup-(2025-guide))
- [How to Meter OpenAI API and ChatGPT Usage | OpenMeter](https://openmeter.io/blog/how-to-meter-openai-and-chatgpt-api-usage)
- [Usage-Based Billing For AI Agents, SaaS And Developer Tools](https://www.chargebee.com/blog/usage-based-billing-reimagined-for-the-age-of-ai/)
- [Optimizing Usage-Based Billing for AI Services](https://www.subscriptionflow.com/2025/04/usage-based-billing-for-ai-services/)

### Kubernetes & GPU Scheduling
- [Kubernetes and GPU: The Complete Guide to AI/ML Acceleration in 2025](https://collabnix.com/kubernetes-and-gpu-the-complete-guide-to-ai-ml-acceleration-in-2025/)
- [Kubernetes and AI: Mastering ML Workloads in 2025](https://collabnix.com/kubernetes-and-ai-the-ultimate-guide-to-orchestrating-machine-learning-workloads-in-2025/)
- [Kubernetes GPU Scheduling in 2025: Practical Patterns](https://debugg.ai/resources/kubernetes-gpu-scheduling-2025-kueue-volcano-mig)
- [GPU Scheduling in Kubernetes: Resource Management Guide](https://collabnix.com/gpu-scheduling-resource-management-in-kubernetes/)
- [NVIDIA GPU Operator Explained: Simplifying GPU Workloads on Kubernetes](https://sagar-parmar.medium.com/nvidia-gpu-operator-explained-simplifying-gpu-workloads-on-kubernetes-436e0a60d0ac)
- [KubeCon 2025: How Kubernetes Is Powering the Future of AI Workloads](https://itgix.com/blog/kubecon-2025-kubernetes-is-powering-ai-workloads/)
- [AI Conformant Azure Kubernetes Service (AKS) clusters | AKS Engineering Blog](https://blog.aks.azure.com/2025/12/05/kubernetes-ai-conformance-aks)
- [AI Workloads on Kubernetes: Future Trends for 2025](https://collabnix.com/running-ai-workloads-on-kubernetes-in-2025/)
- [AI/ML in Kubernetes Best Practices: The Essentials | Wiz](https://www.wiz.io/academy/ai-ml-kubernetes-best-practices)

### API Gateways
- [6 Best Open-Source API Gateways | Nordic APIs](https://nordicapis.com/6-open-source-api-gateways/)
- [Kong Gateway: Most Trusted Open Source API Gateway](https://konghq.com/products/kong-gateway)
- [How to choose the right API Gateway for your platform: Comparison of Kong, Tyk, KrakenD, Apigee](https://www.moesif.com/blog/technical/api-gateways/How-to-Choose-The-Right-API-Gateway-For-Your-Platform-Comparison-Of-Kong-Tyk-Apigee-And-Alternatives/)
- [Tyk vs Kong: Which API Gateway Should You Choose in 2025?](https://apidog.com/blog/tyk-vs-kong/)
- [Multi-Tenant API Gateway Optimizations for managed K8s clusters](https://umatechnology.org/multi-tenant-api-gateway-optimizations-for-managed-k8s-clusters-powered-by-open-source-stacks/)
- [Exploring Seven Robust Open-Source API Gateways](https://amadla.medium.com/exploring-seven-robust-open-source-api-gateways-89c284dbd1eb)

### Billing Platforms
- [GitHub - getlago/lago: Open Source Metering and Usage Based Billing API](https://github.com/getlago/lago)
- [Lago - Metering & Usage-Based Billing](https://www.getlago.com/)
- [OpenMeter - Open Source Billing and Usage Metering](https://openmeter.io/)
- [Best Open Source Alternatives to Traditional Billing Platforms](https://flexprice.io/blog/best-open-source-alternatives-to-traditional-billing-platforms)

### ML Platform Tools
- [Build a ML platform with Kubeflow and Ray on GKE | Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/build-a-ml-platform-with-kubeflow-and-ray-on-gke)
- [Kubeflow Architecture](https://www.kubeflow.org/docs/started/architecture/)
- [Kubernetes for ML: A Developer's Practical Guide](https://discoposse.com/2025/12/01/kubernetes-for-ml-a-developers-practical-guide/)
- [Best Open-Source AI Platforms for 2025](https://greennode.ai/blog/best-open-source-ai-platforms)
- [Streamlining Model Lifecycle with KubeRay](https://www.cloudraft.io/blog/streamling-model-lifecycle-with-kuberay)
- [Best 10 Open-Source MLOps Tools to Optimize & Manage ML | Deepchecks](https://www.deepchecks.com/best-10-open-source-mlops-tools-to-optimize-manage-ml/)
- [MultiGPU Kubernetes Cluster for Scalable and Cost-Effective Machine Learning](https://www.datamax.ai/post/multigpu-kubernetes-with-ray)

### AWS SaaS Builder Toolkit
- [GitHub - aws-samples/aws-saas-factory-eks-reference-architecture](https://github.com/aws-samples/aws-saas-factory-eks-reference-architecture)
- [GitHub - aws-samples/saas-reference-architecture-ecs](https://github.com/aws-samples/saas-reference-architecture-ecs)
- [SaaS Builder Toolkit for AWS + ARC by SourceFuse](https://www.sourcefuse.com/resources/blog/saas-builder-toolkit-for-aws-arc-by-sourcefuse/)
- [Let's Architect! Building multi-tenant SaaS systems | AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/lets-architect-building-multi-tenant-saas-systems/)
- [Building a Multi-Tenant SaaS Solution Using AWS Serverless Services](https://aws.amazon.com/blogs/apn/building-a-multi-tenant-saas-solution-using-aws-serverless-services/)

### Model Serving
- [Top 10 AI Model Serving Frameworks Tools in 2025](https://www.devopsschool.com/blog/top-10-ai-model-serving-frameworks-tools-in-2025-features-pros-cons-comparison/)
- [Frameworks for serving Machine Learning Models on Kubernetes](https://bigdatarepublic.nl/articles/frameworks-for-serving-machine-learning-models-on-kubernetes/)
- [Machine Learning Model Serving Tools Comparison - KServe, Seldon Core, BentoML](https://xebia.com/blog/machine-learning-model-serving-tools-comparison-kserve-seldon-core-bentoml/)
- [Deploying Open-Source LLMs on Kubernetes: A Comprehensive Guide](https://innitor.ai/blog/deploying-open-source-llms-on-kubernetes-a-comprehensive-guide)
- [GitHub - kserve/kserve: Standardized Distributed Generative and Predictive AI Inference Platform](https://github.com/kserve/kserve)
- [Announcing KServe v0.15: Advancing Generative AI Model Serving | CNCF](https://www.cncf.io/blog/2025/06/18/announcing-kserve-v0-15-advancing-generative-ai-model-serving/)

### Observability
- [AI and observability | Grafana Cloud](https://grafana.com/products/cloud/ai-tools-for-observability/)
- [Grafana: The open and composable observability platform](https://grafana.com/)
- [Grafana Cloud AI Observability](https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/)
- [What is Prometheus? | Grafana Cloud documentation](https://grafana.com/docs/grafana-cloud/introduction/what-is-observability/prometheus/)
- [Monitor your generative AI app with the AI Observability solution in Grafana Cloud](https://grafana.com/blog/2024/10/21/monitor-your-generative-ai-app-with-the-ai-observability-solution-in-grafana-cloud/)
- [Databricks observability using Grafana and Prometheus](https://community.databricks.com/t5/technical-blog/databricks-observability-using-grafana-and-prometheus/ba-p/96849)

### Rate Limiting
- [Rate Limiting | Redis](https://redis.io/glossary/rate-limiting/)
- [Design a Distributed Scalable API Rate Limiter](https://systemsdesign.cloud/SystemDesign/RateLimiter)
- [From Token Bucket to Sliding Window: Pick the Perfect Rate Limiting Algorithm](https://api7.ai/blog/rate-limiting-guide-algorithms-best-practices)
- [Rate limiting with Redis | Ramp Builders Blog](https://builders.ramp.com/post/rate-limiting-with-redis)
- [Rate limiting with Redis: An essential guide](https://foojay.io/today/rate-limiting-with-redis-an-essential-guide/)
- [Token Bucket Rate Limiter (Redis & Java)](https://medium.com/redis-with-raphael-de-lio/token-bucket-rate-limiter-redis-java-8cd42f3f8a34)
- [Node.js API Rate Limiting Explained: Token Bucket & Leaky Bucket Techniques](https://www.c-sharpcorner.com/article/node-js-api-rate-limiting-explained-token-bucket-leaky-bucket-techniques/)

### Security
- [OWASP Cloud Tenant Isolation | OWASP Foundation](https://owasp.org/www-project-cloud-tenant-isolation/)
- [SaaS Application Security Guide: Issues, Best Practices, and Examples](https://relevant.software/blog/saas-application-security-guide/)
- [Implementing Strong Cross-Tenant Security Boundaries](https://www.linkedin.com/pulse/implementing-strong-cross-tenant-security-boundaries-coguard-4beoc)
- [How Multi-Tenant Data Isolation Enhances Cloud Security](https://ones.com/blog/multi-tenant-data-isolation-cloud-security-best-practices/)
- [Resource isolation with multiple tenants - Microsoft Entra](https://learn.microsoft.com/en-us/entra/architecture/secure-multiple-tenants)
- [Multi-Tenancy Cloud Security: Definition & Best Practices](https://www.esecurityplanet.com/cloud/multi-tenancy-cloud-security/)

---

**End of Research Document**
