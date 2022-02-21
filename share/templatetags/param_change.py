from django import template

register = template.Library()

#urlreplaceというテンプレートタグを作り、引数としてrequestオブジェクト、クエリストリングのキー、クエリストリングの値
#https://docs.djangoproject.com/ja/4.0/howto/custom-template-tags/
#https://docs.djangoproject.com/ja/4.0/howto/custom-template-tags/#writing-custom-template-tags


#この@register.simple_tag()はデコレータ。下記関数にテンプレートタグとしての機能を追加している。クラスの継承みたいなものと考えると良い
#https://qiita.com/mtb_beta/items/d257519b018b8cd0cc2e

@register.simple_tag()
def url_replace(request, field, value):

    #request.GETの内容をコピーする
    dict_           = request.GET.copy()

    #指定されたキーに対応する値をvalueにする。
    dict_[field]    = value

    #クエリストリングで返却する。
    return dict_.urlencode()

