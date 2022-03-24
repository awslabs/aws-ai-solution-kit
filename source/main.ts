#!/usr/bin/env node
import 'source-map-support/register';
import {App} from '@aws-cdk/core';
import {BootstraplessStackSynthesizer} from 'cdk-bootstrapless-synthesizer';
// import {PornImageStack} from './porn-image/porn-image';
// import {InferOCRStack} from './infer-ocr/infer-ocr';
// import {HumanSegStack} from './human-seg/human-seg';
// import {SuperResolutionStack} from './super-resolution/super-resolution';
// import {SuperResolutionInf1Stack} from './super-resolution-inf1/super-resolution-inf1';
// import {SuperResolutionGpuStack} from './super-resolution-gpu/super-resolution-gpu';
// import {OCRBusinessLicenseSolutionCDKStack} from './ocr-cn-business-license/template/ocr-business-license-cdk-stack';
// import {AISolutionKitStack} from './api-deployment/ai-solution-kit-stack';
import {OCRShippedFromSolutionCDKStack} from './ocr-shipped-from/template/ocr-shipped-from-cdk-stack';


const app = new App();
// new PornImageStack(app, "AIKits-Porn-Image-Detection-Stack", {synthesizer: synthesizer()});
// new InferOCRStack(app, "AIKits-Infer-OCR-Stack", {synthesizer: synthesizer()});
// new HumanSegStack(app, "AIKits-Human-Seg-Stack", {synthesizer: synthesizer()});
// new SuperResolutionStack(app, "AIKits-Super-Resolution-Stack", {synthesizer: synthesizer()});
// new SuperResolutionInf1Stack(app, "AIKits-Super-Resolution-Inf1-Stack", {synthesizer: synthesizer()});
// new SuperResolutionGpuStack(app, "AIKits-Super-Resolution-GPU-Stack", {synthesizer: synthesizer()});
// new OCRBusinessLicenseSolutionCDKStack(app, "AIKits-OCR-CN-Business-License-Stack", {synthesizer: synthesizer()});
// new AISolutionKitStack(app, "AISolutionKitStack3", {synthesizer: synthesizer()});
new OCRShippedFromSolutionCDKStack(app, "AIKits-OCR-Shipped-From-Stack", {synthesizer: synthesizer()});

app.synth()

function synthesizer() {
    return process.env.USE_BSS ? new BootstraplessStackSynthesizer() : undefined;
}