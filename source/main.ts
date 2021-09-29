#!/usr/bin/env node
import 'source-map-support/register';
import {App} from '@aws-cdk/core';
import {BootstraplessStackSynthesizer} from 'cdk-bootstrapless-synthesizer';
import {PornImageStack} from './porn-image/porn-image';
import {InferOCRStack} from './infer-ocr/infer-ocr';
import {HumanSegStack} from './human-seg/human-seg';
import {SuperResolutionStack} from './super-resolution/super-resolution';
import {SuperResolutionInf1Stack} from './super-resolution-inf1/super-resolution-inf1';
import {SuperResolutionGpuStack} from './super-resolution-gpu/super-resolution-gpu';


const app = new App();
new PornImageStack(app, "AIKits-Porn-Image-Detection-Stack", {synthesizer: synthesizer()});
new InferOCRStack(app, "AIKits-Infer-OCR-Stack", {synthesizer: synthesizer()});
new HumanSegStack(app, "AIKits-Human-Seg-Stack", {synthesizer: synthesizer()});
new SuperResolutionStack(app, "AIKits-Super-Resolution-Stack", {synthesizer: synthesizer()});
new SuperResolutionInf1Stack(app, "AIKits-Super-Resolution-Inf1-Stack", {synthesizer: synthesizer()});
new SuperResolutionGpuStack(app, "AIKits-Super-Resolution-GPU-Stack", {synthesizer: synthesizer()});
app.synth()

function synthesizer() {
    return process.env.USE_BSS ? new BootstraplessStackSynthesizer() : undefined;
}