FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["NetDemo/NetDemo.csproj", "NetDemo/"]
RUN dotnet restore "NetDemo/NetDemo.csproj"
COPY . .
RUN dotnet publish "NetDemo/NetDemo.csproj" -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
ARG APP_UID=1000
USER $APP_UID
ENTRYPOINT ["dotnet", "NetDemo.dll"]
