import { CfnCondition, CfnParameter, Construct, Fn } from "@aws-cdk/core";

export interface FeatureConditionProps {
    readonly featureName: string;
    readonly featureDescription: string;

    /**
     * @default 'no'
     */
    readonly defaultValue: string;
}

// const ocrFeatureCondition = new FeatureConditionConstruct(this, 'general-ocr', {
//     featureName: 'GeneralOCR',
//     featureDescription : 'Recognize text from images, and return the coordinate position and confidence scores of the text. This solution supports the recognition of simplified Chinese, traditional Chinese, English and numbers.',
//     defaultValue: 'no',
// });
export class FeatureConditionConstruct extends Construct {
    public condition: CfnCondition
    constructor(scope: Construct, id: string, props: FeatureConditionProps) {

        super(scope, id);
        const feature = new CfnParameter(this, `Install ${props.featureName}`, {
            default: props.defaultValue,
            type: 'String',
            description: `Install ${props.featureName} feature.`,
            allowedValues: ['yes', 'no']
        });

        this.condition = new CfnCondition(
            this,
            `${props.featureName}-condition`,
            {
                expression: Fn.conditionEquals(feature, 'yes')
            }
        )
    }
}
