from module import app
import module.service.nlpService as NlpService
import module.util.routeUtil as RouteUtil


@app.route('/tokenizer-postagger', methods=['POST'])
@RouteUtil.restrict(['ADMIN', 'MODULE'])
@RouteUtil.safe_result()
def tokenizer_postagger():

    return RouteUtil.data_to_json_response(
        NlpService.tokenizer_postagger(RouteUtil.safe_json_get('text'),
                                       RouteUtil.safe_json_get('lang'),
                                       RouteUtil.safe_json_get('filter'),
                                       RouteUtil.safe_json_get('smartSentenceSegmentation'),
                                       RouteUtil.safe_json_get('smartWordSegmentation')))


