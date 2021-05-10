---
layout: post
title: Good Data Scientist, Bad Data Scientist
author: ianwhitestone
summary: What separates a good Data Scientist from a bad one?
comments: False
---

{% include head.html %}

*... motivated by the [Ben Horowitz blog / rant](https://a16z.com/2012/06/15/good-product-managerbad-product-manager/). Opinions are my own.*

<hr>

At their core, data scientists exist to create business value with data. The ways in which value is generated will vary largely company to company, and even team to team. For products or business teams that are early in their lifecycle, this will often take the form of building up basic analytical foundations. The team is likely blind to aspects of the product performance, user behaviour or total addressable market. It is your job to guide them. For others, your product may be more mature and well understood, with established data foundations. Opportunities to enrich the product experience with data driven features may arise. It is up to you to understand how you can drive the most value.

There's a wide array of work a data scientist (DS) can be involved with. This post aims to address the common elements that will make a great DS, or a bad one, no matter what part of the stack you are working on. 

There's also a core set of technical chops every DS must have: SQL, an analytical mindset, fluency in a programming language like Python or R, an understanding of statistics, and machine learning methods, if the product calls for it. But that is only half the story. If we condition on people who have those required baseline skills, this post is what separates the good from the bad. 

# Good DS / Bad DS

Good DS is obsessed with solving business problems. They relentlessly search for them, and then bring out the right tool once found. Bad DS is obsessed with applying a specific technology or tool. They'll orient their search for problems around the tool they are looking to use.

Good DS has a deep understanding of data lineage & sourcing, and will often build these pipelines themselves. Bad DS thinks it is someone else's job.

Good DS understands the inherent limitations behind a stat. They recognize the underlying biases and recommend other, potentially non-quantitative sources that should be consulted. Bad DS treats that stat as the only thing that should be consulted or trusted.

Good DS thinks from first principles. Bad DS accepts everything they have heard or seen as the ground truth, or the best way to do something.

Good DS adjusts their messaging based on their audience. They understand when to provide context and how deep they should go. Bad DS delivers the same message regardless.

Good DS is curious. They venture well outside the confines of their domain in order to seek broader context and understanding. Bad DS tries to abstract everything against the domain or data they are already familiar with, and in doing so often miss the bigger picture.

Good DS understands marginal return on effort. They know when adding a 1% lift in accuracy will have a high enough ROI to justify spending weeks trying to achieve it. Or whether making a statistic 1% more accurate will actually change any decisions. Bad DS keeps working until they run out of time or someone tells them to stop. 

Good DS starts simple, ships, and then iterates. Bad DS starts with the most advanced technique they know.

Good DS is constantly learning & evolving their toolbox. Bad DS stagnates and sticks with what they know.

Good DS is an effective bridge between different disciplines, connecting business and tech organizations cohesively and thus becoming central nodes in the information exchange. Bad DS are a side node in the team or organization, easily ignorable.

Good DS knows where to find information, and doesn't stop when their first attempt fails. Bad DS gets blocked as soon as they can't find what they're looking for.

Good DS is a generalist. They can draw from different skills & tools based on the problem at hand. Bad DS has a narrow set of skills and tools they can apply.

Good DS generates lots of different hypotheses and tests them. They ask lots of questions. Bad DS only thinks of a few and stops when they turn out to be wrong.

Good DS understands the basics of web technology and their company's underlying tech stack. Bad DS treats this as a black box that is outside of their domain and therefore shouldn't be learned.

Good DS has a deep understanding of the product or service their company offers. They understand the company business model and how their team or group contributes to the P&L. Bad DS doesn't think this is necessary.

Good DS gets their hands dirty. They actively use their product or service. They test the product to identify pain points, or understand how the underlying data models work. They listen, or even talk to customers. Bad DS doesn't see the value in this or thinks it's someone else's job.

Good DS actively proposes work. They think beyond what a stakeholder may ask and generate new ideas for how data can add value. They push instead of pull. Bad DS operates purely as a question & answer service.

<br>
<br>
<hr>

Thanks to [@javier](https://twitter.com/infrahumano) for providing valuable feedback & suggestions.