import logging
import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q

from .models import Charge
from apps.users.models import UserProfile

# Create your views here.


logger = logging.getLogger('management')


@login_required(login_url="login.html")
def index(request):
    """
    首页
    :param request:
    :return:
    """
    logger.info('request index ....')
    return render(request, 'base.html')


class ChargeListView(ListView):
    """
    收费信息列表
    """
    template_name = 'charge.html'
    model = Charge
    queryset = Charge.objects.filter(in_arrears='欠费')
    ordering = ('-arrears_time',)

    def get_context_data(self, **kwargs):
        context = {
            "charge_active": "active",
            "charge_list_active": "active",
            "charge_list": self.queryset[:10]
        }
        kwargs.update(context)
        logger.info('ChargeListView.get_context_data.queryset={}'.format(self.queryset.values()))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        """
        收费信息查询
        """
        self.queryset = super().get_queryset()
        if self.request.GET.get('name'):
            query = self.request.GET.get('name', None)
            print(query)
            logger.info('ChargeListView.get_queryset.name={}'.format(query))
            self.queryset = self.queryset.filter(
                Q(account_number__icontains=query) | Q(address__icontains=query) | Q(write_book__icontains=query),
                Q(in_arrears='欠费')).order_by('id')
            print(self.queryset)
        return self.queryset


@login_required(login_url="login.html")
def charges(request):
    """
    收费
    :param request:
    :return:
    """
    id_list = request.POST.getlist('id')
    if not id_list:
        return render(request, 'chargedetial.html', {'err_msg': '请选中要收费的户号'})
    money = request.POST.get('money').strip()
    logger.info('charges.id_list={},money={}'.format(id_list, money))
    arrears_sum = 0.0
    query_list = []

    context = {
        "charge_active": "active",
        "charge_list_active": "active"
    }
    for ids in id_list:
        arrears_sum += Charge.objects.get(pk=ids).arrears
        print(Charge.objects.get(pk=ids).arrears)
        print(Charge.objects.get(pk=ids))
        logger.info('charges.arrears_sum'.format(arrears_sum))
    try:
        surplus = Decimal(Decimal(money) - Decimal(arrears_sum)).quantize(Decimal('0.00'))
    except ValueError as e:
        err_dict = {
            'err_msg': "输入金额格式不对"
        }
        logger.info("charges.err_msg='输入金额格式不对'")
        context.update(err_dict)
        return render(request, 'chargedetial.html', context)
    if surplus < 0:
        err_dict = {
            'err_msg': "金额不足"
        }
        logger.info("charges.err_msg='金额不足'")
        context.update(err_dict)
        return render(request, 'chargedetial.html', context)
    user = UserProfile.objects.get(username=request.user.username)
    for ids in id_list:
        arrears = Charge.objects.get(pk=ids).arrears
        Charge.objects.filter(id=ids).update(in_arrears='已收费', charges=arrears,
                                             charge_time=datetime.now(), cashier=user)
        update_charge = Charge.objects.get(id=ids)
        query_list.append(update_charge)
    logger.info("charges.query_list={}".format(query_list))
    query_dict = {
        'query_list': query_list,
        'err_msg': '结余：' + str(surplus) + '元'
    }
    context.update(query_dict)
    return render(request, 'chargedetial.html', context)


class QueryListView(ListView):
    """
    收费信息查询
    """
    template_name = 'query.html'
    model = Charge
    queryset = Charge.objects.filter(charge_time__isnull=False)
    ordering = ('charge_time',)
    JsonData = None
    types = None
    summary_title = ''

    def get_context_data(self, **kwargs):
        if self.queryset and len(self.queryset) > 10:
            self.queryset = self.queryset[:10]
        context = {
            "charge_active": "active",
            "query_active": "active",
            "query_list": self.queryset,
            'JsonData': json.dumps(self.JsonData, ensure_ascii=False),
            'types': self.types,
            'summary_title': self.summary_title
        }
        print('Jsondata:', self.JsonData)
        logger.info('QueryListView.get_context_data.JsonData={}'.format(json.dumps(self.JsonData, ensure_ascii=False)))
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        """
        资产信息 查询功能
        """
        self.JsonData = []
        self.queryset = super().get_queryset()
        types = self.request.GET.get('types')
        self.types = types
        start_time = self.request.GET.get('start_time')
        end_time = self.request.GET.get('end_time')
        logger.info('QueryListView.get_queryset.types={},start_time={},end_time={}'.format(types, start_time, end_time))
        if not start_time:
            return self.queryset

        start_time = datetime.strptime(start_time, '%Y-%m-%d')
        end_time = datetime.strptime(end_time, '%Y-%m-%d') + timedelta(days=1, hours=0, minutes=0, seconds=0)

        if start_time and types == '-1':
            self.queryset = self.queryset.filter(Q(charge_time__gte=start_time), Q(charge_time__lte=end_time),
                                                 Q(in_arrears='已收费')).order_by('charge_time')
        elif types == 'cashier':
            self.queryset = self.queryset.filter(Q(charge_time__gte=start_time), Q(charge_time__lte=end_time),
                                                 Q(in_arrears='已收费')).order_by('cashier')
            self.summary_title = "历史欠费收费明细(按收款人汇总)"
        elif types == 'bill_manager':
            self.queryset = self.queryset.filter(Q(charge_time__gte=start_time), Q(charge_time__lte=end_time),
                                                 Q(in_arrears='已收费')).filter(bill_manager__isnull=False).order_by(
                'bill_manager')
            self.summary_title = "历史欠费收费明细(按票据管理人汇总)"

        for item in self.queryset.select_related():
            info = dict()
            info['rowid'] = item.id
            info['cashier'] = item.cashier.name
            info['write_book'] = item.write_book
            info['account_number'] = item.account_number
            info['account_name'] = item.account_name
            info['arrears'] = item.arrears
            info['arrears_time'] = item.arrears_time.strftime('%Y-%m-%d %H:%M:%S')
            info['charges'] = item.charges
            info['charge_time'] = item.charge_time.strftime('%Y-%m-%d %H:%M:%S')
            info['bill_manager'] = item.bill_manager.name
            info['in_arrears'] = item.in_arrears
            self.JsonData.append(info)
        return self.queryset


class SummaryListView(ListView):
    """
     欠费汇总
     """
    template_name = 'summary.html'
    model = Charge
    queryset = Charge.objects.filter(in_arrears='欠费')
    ordering = ('-arrears_time',)
    JsonData = None
    write_book = None
    bill_manager = None
    query = None
    summary_list_str = ''
    types = ''

    def get_context_data(self, **kwargs):
        write_book_list = Charge.objects.filter(in_arrears='欠费').values('write_book').distinct()
        bill_manager_list = Charge.objects.filter(in_arrears='欠费').values('bill_manager__name').distinct()
        if self.queryset and len(self.queryset) > 10:
            self.queryset = self.queryset[:10]
        context = {
            "charge_active": "active",
            "summary_list_active": "active",
            "summary_list": self.queryset,
            "write_book_list": write_book_list,
            "bill_manager_list": bill_manager_list,
            "summary_list_str": self.summary_list_str,
            "types": self.types,
            "JsonData": json.dumps(self.JsonData, ensure_ascii=False)
        }
        logger.info('SummaryListView.get_context_data.summary_list={}'.format(self.queryset))
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        """
        欠费信息 查询功能
        """
        self.JsonData = []
        self.queryset = super().get_queryset()
        write_book = self.request.GET.get('write_book')
        self.write_book = write_book
        bill_manager = self.request.GET.get('bill_manager')
        self.bill_manager = bill_manager
        query = self.request.GET.get('name', None)
        self.query = query
        start_time = self.request.GET.get('start_time')
        end_time = self.request.GET.get('end_time')
        types = self.request.GET.get('types')
        self.types = types
        logger.info('SummaryListView.get_queryset.write_book={},bill_manager={},start_time={},end_time={}'.format(
            write_book, bill_manager, start_time, end_time))
        if start_time is None and write_book is None and bill_manager is None:
            return self.queryset
        if start_time:
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
            end_time = datetime.strptime(end_time, '%Y-%m-%d') + timedelta(days=1, hours=0, minutes=0, seconds=0)
            self.queryset = self.queryset.filter(Q(arrears_time__gte=start_time),
                                                 Q(arrears_time__lte=end_time)).order_by('-arrears_time')

        elif self.write_book != '-1':
            self.queryset = self.queryset.filter(Q(write_book=self.write_book), Q(in_arrears='欠费'))

        elif self.bill_manager != '-1':
            user = UserProfile.objects.filter(name=self.bill_manager)[0].id
            self.queryset = self.queryset.filter(bill_manager=int(user))

        elif self.query:
            logger.info('ChargeListView.get_queryset.name={}'.format(query))
            self.queryset = self.queryset.filter(
                Q(account_number=query) | Q(address__icontains=query) | Q(write_book__icontains=query),
                Q(in_arrears='欠费')).order_by('id')

        elif self.types == 'write_book_summary':
            self.queryset = self.queryset.filter(Q(in_arrears='欠费')).order_by('write_book')
            self.summary_list_str = '历史欠费明细(按抄表册汇总)'

        elif self.types == 'bill_manager_summary':
            self.queryset = self.queryset.filter(Q(in_arrears='欠费')).filter(bill_manager__isnull=False).order_by(
                'bill_manager')
            self.summary_list_str = '历史欠费明细(按票据管理人汇总)'

        elif self.types == 'arrears_time_summary':
            self.queryset = self.queryset.filter(Q(in_arrears='欠费')).order_by('-arrears_time')
            self.summary_list_str = '历史欠费明细(按欠费时间汇总)'

        for item in self.queryset.select_related():
            info = dict()
            info['rowid'] = item.id
            info['write_book'] = item.write_book
            info['account_number'] = item.account_number
            info['account_name'] = item.account_name
            info['arrears'] = item.arrears
            info['user_phone'] = item.user_phone
            info['arrears_time'] = item.arrears_time.strftime('%Y-%m-%d %H:%M:%S')
            info['address'] = item.address.replace('山西省阳泉市平定县冠山镇', '')
            info['charges'] = item.charges
            info['bill_manager'] = item.bill_manager.name
            self.JsonData.append(info)
            if self.types == 'write_book_summary' or self.types == 'bill_manager_summary' or self.types == 'arrears_time_summary':
                self.queryset = None

        return self.queryset


def login_view(request):
    """
    登录
    :param request:
    :return:
    """
    error_msg = '用户名或密码错误,请重试!'
    context = {'error_msg': error_msg}
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        user = request.POST.get('username')
        password = request.POST.get('password')
        auth = authenticate(request, username=user, password=password)
        if auth is not None:
            if auth.is_active:
                login(request, auth)
                request.session['is_login'] = True
                logger.info('login_view.user={},login success'.format(user))
                return redirect('index.html')
            else:
                return render(request, 'login.html', context)
        else:
            return render(request, 'login.html', context)


def logout_view(request):
    """
    退出
    :param request:
    :return:
    """
    user = request.user
    logout(request)
    logger.info('logout_view.user={},logout success'.format(user))
    return redirect('login.html')
