Field-by-field checklist
| Field | Purpose | Typical Values / Tips |
|-------|---------|-----------------------|
| **concept_id** | File-safe slug.<br>Use lowercase with underscores. | `neural_networks` |
| **name** | Human-readable title. | Neural Networks |
| **category** | Broad grouping for navigation. | See taxonomy below. |
| **complexity** | How hard for a motivated learner? | beginner / medium / advanced |
| **last_updated** | ISO date you last edited the file.<br>Auto-fill with today’s date or your CI pipeline. | 2025-06-13 |
| **evolution_rate** | How quickly the topic changes. | slow (`linear_regression`) · moderate (`mlops`) · fast (`diffusion_models`) |
| **description** | One-liner elevator pitch. | Keep it < 140 chars so it fits tooltips. |
| **key_components** | Atomic pieces you’d teach first. | 3-8 noun phrases. |
| **properties** | Core characteristics / what makes it special. | 3-6 bullet points. |
| **common_misconceptions** | Myths executives & newcomers believe. | At least 2. |
| **prerequisite_concepts** | Links (`concept_id` values) the user should already know. | e.g. `statistics`, `linear_algebra` |
| **related_concepts** | Lateral links for graph navigation. | e.g. `deep_learning`, `cnn` |


Suggested taxonomy & defaults:
ai_fundamentals
  ├─ core_math                  # linear_algebra, probability_and_statistics …
  ├─ machine_learning_algorithms
  ├─ deep_learning_architectures
  ├─ nlp
  ├─ computer_vision
  ├─ reinforcement_learning
  ├─ data_engineering
  ├─ mlops
  ├─ fairness_ethics_safety
  ├─ business_strategy
  ├─ industry_use_cases
  ├─ cutting_edge

Exhaustive List:
1. Foundations & Big-Picture Context
artificial_intelligence_overview.yaml
history_of_ai.yaml
philosophy_of_ai.yaml
turing_test.yaml
agi_and_superintelligence.yaml
emergent_behaviors.yaml

2. Mathematics & Probability for AI
linear_algebra_for_ml.yaml
calculus_for_ml.yaml
probability_and_statistics.yaml
information_theory.yaml
optimization_methods.yaml

3. Data & Preparation
data_preprocessing.yaml
feature_engineering.yaml
data_augmentation.yaml
data_labeling.yaml
synthetic_data.yaml
missing_data_handling.yaml
data_versioning.yaml
data_governance.yaml
data_quality.yaml
data_lineage.yaml
feature_stores.yaml

4. Core Machine-Learning Paradigms
supervised_learning.yaml
unsupervised_learning.yaml
semi_supervised_learning.yaml
self_supervised_learning.yaml
transfer_learning.yaml
multi_task_learning.yaml
meta_learning.yaml
active_learning.yaml
online_learning.yaml
continual_learning.yaml
federated_learning.yaml
reinforcement_learning_from_human_feedback.yaml
zero_shot_learning.yaml

5. Classical ML Algorithms & Techniques
linear_regression.yaml
logistic_regression.yaml
naive_bayes.yaml
decision_trees.yaml
random_forests.yaml
gradient_boosting.yaml
support_vector_machines.yaml
k_nearest_neighbors.yaml
k_means_clustering.yaml
hierarchical_clustering.yaml
principal_component_analysis.yaml
independent_component_analysis.yaml
gaussian_processes.yaml
bayesian_networks.yaml
hidden_markov_models.yaml

6. Deep-Learning Building Blocks
neural_networks.yaml (already on your list)
deep_learning.yaml (already on your list)
convolutional_neural_networks.yaml
recurrent_neural_networks.yaml
long_short_term_memory.yaml
gated_recurrent_units.yaml
attention_mechanisms.yaml
transformers.yaml (already on your list)
graph_neural_networks.yaml
autoencoders.yaml
variational_autoencoders.yaml
generative_adversarial_networks.yaml
diffusion_models.yaml
mixture_of_experts.yaml
sparse_models.yaml

7. Natural-Language Technologies
natural_language_processing.yaml (already on your list)
language_modeling.yaml
large_language_models.yaml (already on your list)
text_classification.yaml
sentiment_analysis.yaml
machine_translation.yaml
question_answering.yaml
summarization.yaml
conversational_ai.yaml
information_retrieval.yaml
named_entity_recognition.yaml
speech_recognition.yaml
speech_synthesis.yaml
text_generation.yaml
retrieval_augmented_generation.yaml (rag_systems.yaml)
prompt_engineering.yaml (already on your list)
chain_of_thought.yaml (already on your list)
few_shot_learning.yaml (already on your list)
in_context_learning.yaml

8. Vision, Audio & Multimodal
computer_vision.yaml (already on your list)
image_classification.yaml
object_detection.yaml
image_segmentation.yaml
pose_estimation.yaml
video_analysis.yaml
optical_character_recognition.yaml
3d_vision.yaml
image_generation.yaml
multimodal_learning.yaml
audio_analysis.yaml
music_generation.yaml

9. Reinforcement-Learning Variants
reinforcement_learning.yaml (already on your list)
actor_critic_methods.yaml
value_based_methods.yaml
policy_gradient_methods.yaml
model_based_rl.yaml
multi_agent_rl.yaml
hierarchical_rl.yaml
inverse_rl.yaml
offline_rl.yaml
safe_rl.yaml

10. Generative & Creative AI
generative_models.yaml
text_to_image.yaml
code_generation.yaml
video_generation.yaml
synthetic_media_ethics.yaml

11. Causal, Symbolic & Hybrid Approaches
causal_inference.yaml
causal_machine_learning.yaml
knowledge_graphs.yaml
neurosymbolic_ai.yaml
planning_and_reasoning.yaml

12. Fairness, Ethics, Trust & Safety
ethics_in_ai.yaml
bias_in_ai.yaml (already on your list)
fairness_in_ai.yaml
explainable_ai.yaml
interpretability_methods.yaml
accountability_in_ai.yaml
privacy_preserving_ai.yaml
differential_privacy.yaml
adversarial_ml.yaml
robustness_and_security.yaml
ai_risk_management.yaml
ai_auditing.yaml
responsible_ai.yaml
eu_ai_act.yaml
ai_policy_and_regulation.yaml

13. ML Engineering & Operations
machine_learning.yaml (already on your list)
mlops.yaml
model_serving.yaml
model_monitoring.yaml
model_compression.yaml
quantization.yaml
pruning.yaml
edge_ai.yaml
distributed_training.yaml
auto_ml.yaml
kubernetes_for_ml.yaml
continuous_integration_ml.yaml
concept_drift.yaml

14. Toolkits, Frameworks & Infrastructure
pytorch.yaml
tensorflow.yaml
jax.yaml
keras.yaml
scikit_learn.yaml
huggingface_transformers.yaml
langchain.yaml
mlflow.yaml
dvc.yaml
ray.yaml
apache_spark_ml.yaml
vector_databases_overview.yaml
faiss_vector_search.yaml
weaviate_vector_search.yaml
pinecone_vector_search.yaml
openai_api.yaml
llama_index.yaml
gpu_computing.yaml
tpu_computing.yaml
fpga_for_ai.yaml

15. Evaluation, Metrics & Experimentation
model_evaluation_metrics.yaml
cross_validation.yaml
hyperparameter_tuning.yaml
benchmarking.yaml
ab_testing_for_ml.yaml
interpretability_metrics.yaml

16. Business, Strategy & Industry Use-Cases
ai_strategy.yaml
roi_of_ai.yaml
ai_product_management.yaml
ai_transformation.yaml
ai_governance.yaml
ai_in_healthcare.yaml
ai_in_finance.yaml
ai_in_energy.yaml
ai_in_manufacturing.yaml
ai_in_marketing.yaml
ai_in_supply_chain.yaml
ai_in_retail.yaml
ai_in_government.yaml
ai_and_future_of_work.yaml
ai_economics.yaml

17. Society, Education & Human Factors
ai_literacy.yaml
human_ai_interaction.yaml
human_in_the_loop.yaml
collaborative_ai.yaml
affective_computing.yaml
ai_for_accessibility.yaml
persuasive_technology.yaml
ai_and_environment.yaml
ai_and_sustainability.yaml
ai_and_law.yaml

18. Cutting-Edge & Interdisciplinary Frontiers
quantum_machine_learning.yaml
biologically_inspired_ai.yaml
spiking_neural_networks.yaml
neuroevolution.yaml
open_ended_learning.yaml
lifelong_learning.yaml
agentic_workflows.yaml
foundation_models.yaml
multi_modal_agents.yaml
autonomous_systems.yaml
self_replicating_ai.yaml

Below is a one-to-one (or many-to-one) mapping that shows where each of the 18 headline categories I suggested earlier naturally fits inside your 12-node taxonomy.

18-category block	Fits under this 12-node root	Why it belongs there / notes
1. Foundations & Big-Picture Context	ai_fundamentals	General orientation, history, AGI, philosophy—all baseline context.
2. Mathematics & Probability for AI	core_math	Linear algebra, calculus, stats, info theory.
3. Data & Preparation	data_engineering	Data cleaning, governance, lineage, feature stores.
4. Core Machine-Learning Paradigms	machine_learning_algorithms	Supervised/unsupervised, transfer, meta-learning, etc.
5. Classical ML Algorithms & Techniques	machine_learning_algorithms	Regression, SVMs, trees, clustering…
6. Deep-Learning Building Blocks	deep_learning_architectures	CNNs, RNNs, VAEs, GANs, diffusion, MoE.
7. Natural-Language Technologies	nlp	LLMs, embeddings, RAG, speech, NER, MT, prompt engineering.
8. Vision, Audio & Multimodal	computer_vision	Image/video tasks, OCR, T2I, multimodal fusion. (Audio could live here or get its own node if you add one.)
9. Reinforcement-Learning Variants	reinforcement_learning	Actor-critic, safe RL, MARL, offline RL.
10. Generative & Creative AI	deep_learning_architectures and nlp/computer_vision	Text-to-image, code generation, video gen—architecturally DL, applied in NLP/CV. Cross-links recommended.
11. Causal, Symbolic & Hybrid Approaches	machine_learning_algorithms and cutting_edge	Causal ML, neuro-symbolic, reasoning—bridges classic & frontier work.
12. Fairness, Ethics, Trust & Safety	fairness_ethics_safety	Bias, privacy, robustness, AI risk, governance.
13. ML Engineering & Operations	mlops	Model serving, monitoring, CI/CD, drift detection, AutoML.
14. Toolkits, Frameworks & Infrastructure	mlops and data_engineering	PyTorch, Ray, vector DBs, GPUs/TPUs. Mostly operational.
15. Evaluation, Metrics & Experimentation	mlops	Benchmarks, cross-validation, A/B testing—core to production practice.
16. Business, Strategy & Industry Use-Cases	business_strategy	ROI, AI product management, sector playbooks.
17. Society, Education & Human Factors	business_strategy and fairness_ethics_safety	AI literacy, HCI, accessibility, future-of-work—where org strategy meets ethics.
18. Cutting-Edge & Interdisciplinary Frontiers	cutting_edge	Quantum ML, spiking nets, agentic workflows—fast-moving research.