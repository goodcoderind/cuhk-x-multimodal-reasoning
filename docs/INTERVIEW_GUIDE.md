# Explaining the project

## A one-minute account

“I worked on the CUHK-X Large Model Track, answering action questions from non-RGB video and motion signals. Starting from an attributed public prediction baseline, the project combined frozen visual features, small supervised models, and rules that made related answers consistent. The best recorded public score was 0.88304; the public rank observed on 15 September was 24 out of 213 teams. The repo shows the reusable components, experiment results, and limitations. Development was AI-assisted, and some inherited baseline predictions remain, so I distinguish the parts I can demonstrate from a full end-to-end reproduction.”

## Be ready to explain these decisions

**Why was frame preprocessing consequential?** A model expecting a square image can center-crop a wide contact sheet and lose the first and last events. Splitting and padding the individual frames preserves their spatial coverage. Temporal sampling remains a separate issue: four intact frames can still miss a brief event.

**Why joint decoding?** Different questions constrain the same underlying activity set. A combination answer that says “drink and phone” should agree with the multi-select answer about those actions. Enumerating a small candidate space allows both model scores and consistency penalties to influence the final choices. A bad constraint can also suppress a correct answer, so the decoder needs evaluation.

**Why hold out people?** Multiple questions can refer to the same recording, and one person can appear in many recordings. Random question splits can let the model see closely related data while fitting and evaluating. A person-based split is a stronger check of transfer, although repeated tuning on that split still overfits development data.

**Why didn't a larger model solve it automatically?** Success depends on what was visible, which moments were sampled, the domain of the imagery, and the answer format. A stronger general model can make different mistakes without improving the aggregate result. The final two-pass HIGH-reasoning ORDER experiment tied the saved direct method at 26/36 and was not submitted.

**What was a useful failure?** The pose audit found that constant confidence values and changing actor-list order could break actor selection. Fixing the input behavior did not automatically improve the trained model: feature changes also change the distribution seen by existing weights. The experiment separated a real software repair from a demonstrated accuracy gain.

**What exactly is reproducible?** The public package runs a synthetic demonstration of actual decoding logic and evaluation safeguards. The optional encoder demonstrates preprocessing and feature extraction with separately supplied weights. The full best-scoring submission still depends on unrecovered inherited prediction generators and private competition artifacts.

## A résumé bullet

> Developed an AI-assisted multimodal action-understanding competition pipeline with frozen visual features, motion summaries, and cross-question consistency; improved an attributed public baseline from 0.77777 to a best recorded 0.88304 public score, and published runnable components with an experiment audit.

Use “public rank 24/213, observed 15 September 2026” only with that date and qualification. Update it when official final standings exist. Do not write “top-15 finalist,” “trained V-JEPA 2,” “fully reproduced 0.88304,” or imply a formal CUHK affiliation.

## Before an interview

Run the demo yourself, read the decoder, and change one synthetic score to see how the selected set changes. Be able to distinguish code you understand and can explain from work that was substantially generated with assistance. A specific explanation of one input bug, one useful model decision, and one failed experiment is more credible than a long list of model names.
