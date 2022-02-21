from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages

#TODO:filterに使用するクエリビルダ
from django.db.models import Q

#TODO:ページネーションを実装させる
from django.core.paginator import Paginator


from .models import Document,Review
from .forms import DocumentForm,ReviewForm

import magic
ALLOWED_MIME = ["image/jpeg", "application/zip", "video/mp4", "application/pdf"]


#CHECK:LoginRequiredMixinをViewと一緒に継承する(多重継承)することで、未認証のユーザーをログインページにリダイレクトすることができる。
class IndexView(LoginRequiredMixin,View):

    def get(self, request, *args, **kwargs):

        context                 = {}

        #ページネーションと検索機能
        if "search" in request.GET:

            #(1)キーワードが空欄もしくはスペースのみの場合、ページにリダイレクト
            if request.GET["search"] == "" or request.GET["search"].isspace():
                return redirect("share:index")

            #(2)キーワードをリスト化させる(複数指定の場合に対応させるため)
            search      = request.GET["search"].replace("　"," ")
            search_list = search.split(" ")

            #(3)クエリを作る
            query       = Q()
            for word in search_list:

                #空欄の場合は次のループへ
                if word == "":
                    continue

                #TIPS:AND検索の場合は&を、OR検索の場合は|を使用する。
                query &= Q(name__contains=word)

            documents = Document.objects.filter(query).order_by("-dt")
            #documents    = Document.objects.filter(name__contains=request.GET["search"]).order_by("-dt")
        else:
            documents = Document.objects.order_by("-dt")

        paginator   = Paginator(documents,2)

        if "page" in request.GET:
            context["documents"]    = paginator.get_page(request.GET["page"])
        else:
            context["documents"]    = paginator.get_page(1)

        return render(request,"share/index.html", context)

    def post(self, request, *args, **kwargs):

        #アップロードファイルが存在しない場合、リダイレクト。
        #想定外の処理をされた場合、return文を実行する。これをアーリーリターン(early return)。
        #メリット:ネストが深くなるのを防ぐ、処理速度が若干速くなる。

        if "content" not in request.FILES:
            messages.error(request, "ファイルがありません")
            return redirect("dojo:index")

        #mimeの取得、mimeをセットしたリクエストをバリデーションする。
        mime    = magic.from_buffer(request.FILES["content"].read(1024), mime=True)

        #TIPS:クライアントから受け取ったリクエストを直接書き換えすることはできない。そのためcopyメソッドでリクエストのコピーを作る。
        copied          = request.POST.copy()
        copied["mime"]  = mime

        #TODO:ユーザーIDをコピーしたリクエストに格納する。その上でバリデーション。
        copied["user"]  = request.user.id


        form = DocumentForm(copied, request.FILES)

        if form.is_valid():
            print("バリデーションOK")
            # 保存する

            if mime in ALLOWED_MIME:
                messages.success(request, "保存に成功しました")
                form.save()
            else:
                messages.error(request, "このファイルは許可されていません")
                print("このファイルは許可されていません")
        else:
            messages.error(request, form.errors)
            print(form.errors)
            print("バリデーションNG")
            print(mime)

        return redirect("share:index")

index   = IndexView.as_view()



#投稿されたファイルの個別ページ
class SingleView(LoginRequiredMixin,View):

    #urls.pyに書かれたpkを引数として受け取り、ファイルを特定する。
    def get(self, request, pk, *args, **kwargs):

        context             = {}
        context["document"] = Document.objects.filter(id=pk).first()
        context["reviews"]  = Review.objects.filter(document=pk).order_by("-dt")

        return render(request,"share/single.html", context)

    def post(self, request, pk, *args, **kwargs):

        #TODO:ここで投稿されたファイルに対するレビューを受け付ける。
        copied  = request.POST.copy()
        copied["user"]      = request.user.id
        copied["document"]  = pk

        form = ReviewForm(copied)

        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            print("バリデーションNG")

        return redirect("share:single", pk)

single  = SingleView.as_view()

